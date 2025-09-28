import sys
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re
import aiohttp
import json

# ==============================
# API: Fear & Greed Index
# ==============================
async def fetch_fear_greed_api():
    """
    Fetch Fear and Greed historical data from CoinMarketCap API
    Note: Requires CoinMarketCap Pro API key
    """
    api_key = "0ec32b61-d462-4be5-92f5-85d4f14ec474"  # User's actual API key
    if api_key == "YOUR_COINMARKETCAP_API_KEY":
        return {
            'error': 'API key not configured',
            'message': 'Please set your CoinMarketCap Pro API key to fetch historical data',
            'endpoint': 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical'
        }
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {
                        'error': f'API request failed with status {response.status}',
                        'response': await response.text()
                    }
    except Exception as e:
        return {
            'error': 'API request failed',
            'exception': str(e)
        }

# ==============================
# Parse Whale Alert Text Content
# ==============================
def parse_whale_alerts(scraped_content: str):
    """
    Extract whale alerts (BTC only) from Whale Alert HTML/text scrape.
    Returns a list of dicts.
    """
    alerts = []
    # Example: "2,500 #BTC (274,372,375 USD) transferred from #Kraken to unknown wallet"
    pattern = re.compile(
        r'(\d[\d,]*)\s+#BTC.*\(([\d,]+)\s+USD\).*transferred from (.*?) to (.*)',
        re.IGNORECASE
    )

    for match in pattern.finditer(scraped_content):
        amount = int(match.group(1).replace(',', ''))
        usd_value = int(match.group(2).replace(',', ''))
        source = match.group(3).strip()
        dest = match.group(4).strip()
        alerts.append({
            "amount_btc": amount,
            "usd_value": usd_value,
            "from": source,
            "to": dest
        })

    return alerts

# ==============================
# Main Scraper Function
# ==============================
async def scrape_and_save():

    # Map short names to URLs/APIs
    site_map = {
        'cc_home': {
            'url': "https://www.cryptocraft.com/",
            'desc': 'CryptoCraft Home'
        },
        'cc_btc': {
            'url': "https://www.cryptocraft.com/market/btcusd",
            'desc': 'CryptoCraft BTC/USD'
        },
        'cc_news': {
            'url': "https://www.cryptocraft.com/news",
            'desc': 'CryptoCraft News'
        },
        'cmc_chart': {
            'url': "https://coinmarketcap.com/charts/fear-and-greed-index/",
            'desc': 'CoinMarketCap Fear & Greed Chart'
        },
        'whale_alert': {
            'url': "https://whale-alert.io/alerts.html",
            'desc': 'Whale Alert Live Alerts'
        }
    }
    api_map = {
        'fear_api': {
            'desc': 'CoinMarketCap Fear & Greed API',
            'func': fetch_fear_greed_api
        }
    }

    # Parse command line args
    enabled_sites = set()
    enabled_apis = set()
    for arg in sys.argv[1:]:
        if arg in site_map:
            enabled_sites.add(arg)
        if arg in api_map:
            enabled_apis.add(arg)

    if not enabled_sites and not enabled_apis:
        print("No sites or APIs selected. Usage:")
        print("  python s.py [cc_home] [cc_btc] [cc_news] [cmc_chart] [whale_alert] [fear_api]")
        return

    all_content = []
    # Scrape selected sites
    if enabled_sites:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                for key in enabled_sites:
                    url = site_map[key]['url']
                    print(f"Accessing: {url}")
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    await page.wait_for_timeout(8000)
                    title = await page.title()
                    content = await page.evaluate('''
                        () => {
                            document.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                            return document.body.innerText;
                        }
                    ''')
                    page_info = {'url': url, 'title': title, 'content': content}
                    all_content.append(page_info)
                    print(f"Content extracted from {url} - Length: {len(content)} characters")
            finally:
                await browser.close()

    # Fetch APIs
    api_data = None
    if 'fear_api' in enabled_apis:
        print("Fetching Fear and Greed historical data from API...")
        api_data = await api_map['fear_api']['func']()

    # Combine scraped content
    scraped_content = ""
    for page in all_content:
        scraped_content += f"=== PAGE: {page['url']} ===\r\n"
        scraped_content += f"TITLE: {page['title']}\r\n"
        scraped_content += "=" * 60 + "\r\n\r\n"
        scraped_content += page['content']
        scraped_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    # Save outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if scraped_content or api_data:
        # Save text
        filename = f"cryptocraft_clean_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(scraped_content)
            if api_data:
                f.write("\n\n=== API DATA: Fear & Greed ===\n")
                f.write(json.dumps(api_data, indent=2))
        print(f"Scraped content saved to {filename}")

        # If Whale Alerts scraped → parse & save JSON
        if 'whale_alert' in enabled_sites:
            whale_data = parse_whale_alerts(scraped_content)
            if whale_data:
                whale_file = f"whale_alerts_{timestamp}.json"
                with open(whale_file, 'w', encoding='utf-8') as wf:
                    json.dump(whale_data, wf, indent=2)
                print(f"Parsed Whale Alerts saved to {whale_file}")
            else:
                print("No Whale BTC transactions found to parse.")
    else:
        print("Nothing to save.")

# ==============================
# Run
# ==============================
if __name__ == "__main__":
    print("Starting scraper...")
    asyncio.run(scrape_and_save())
    print("Done!")
