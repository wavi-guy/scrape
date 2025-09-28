
import sys
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re
import aiohttp
import json

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

    # Parse command line args for enabled sites/APIs
    enabled_sites = set()
    enabled_apis = set()
    for arg in sys.argv[1:]:
        if arg in site_map:
            enabled_sites.add(arg)
        if arg in api_map:
            enabled_apis.add(arg)

    if not enabled_sites and not enabled_apis:
        print("No sites or APIs selected. Usage:")
        print("  python s.py [cc_home] [cc_btc] [cc_news] [cmc_chart] [fear_api]")
        print("  Example: python s.py cc_home fear_api")
        print("  Available:")
        for k, v in site_map.items():
            print(f"    {k}: {v['desc']}")
        for k, v in api_map.items():
            print(f"    {k}: {v['desc']}")
        return

    all_content = []
    # Scrape selected sites
    if enabled_sites:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            page = await context.new_page()
            try:
                for key in enabled_sites:
                    url = site_map[key]['url']
                    print(f"Accessing: {url}")
                    print("Attempting to bypass Cloudflare...")
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    print("Waiting for page to load completely...")
                    await page.wait_for_timeout(8000)
                    title = await page.title()
                    print(f"Page title: {title}")
                    print("Extracting and formatting content...")
                    content = await page.evaluate('''
                        () => {
                            document.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                            let html = document.body.innerHTML || '';
                            html = html.replace(/<\\/tr>/gi, '</tr>\\r\\n');
                            let tempDiv = document.createElement('div');
                            tempDiv.innerHTML = html;
                            let text = tempDiv.textContent || tempDiv.innerText || '';
                            return text;
                        }
                    ''')
                    page_info = {
                        'url': url,
                        'title': title,
                        'content': content
                    }
                    all_content.append(page_info)
                    print(f"Content extracted from {url} - Length: {len(content)} characters")
            finally:
                print("Closing browser...")
                await browser.close()

    # Fetch selected APIs
    api_data = None
    if 'fear_api' in enabled_apis:
        print("Fetching Fear and Greed historical data from API...")
        api_data = await api_map['fear_api']['func']()


    # Combine all scraped page content (to be cleaned)
    scraped_content = ""
    for page in all_content:
        scraped_content += f"=== PAGE: {page['url']} ===\r\n"
        scraped_content += f"TITLE: {page['title']}\r\n"
        scraped_content += "=" * 60 + "\r\n\r\n"
        scraped_content += page['content']
        scraped_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    # Clean up the scraped content in Python (do NOT touch API data)
    if scraped_content:
        print("Cleaning up scraped content...")
        content = scraped_content
        # Remove JavaScript patterns
        content = re.sub(r'window\.\w+\s*=\s*\{[^}]*\}', '', content)
        content = re.sub(r'if\s*\([^)]*\)\s*\{[^}]*\}', '', content)
        # Remove JSON-like patterns
        content = re.sub(r'\{[^}]*"[^"]*"[^}]*\}', '', content)
        content = re.sub(r'\[[^\]]*\]', '', content)
        # Preserve line breaks but clean up excessive whitespace
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'[ \t]+', ' ', line.strip())
            if line:
                words = line.split()
                cleaned_words = []
                for word in words:
                    if word and len(word) > 1:
                        skip_word = False
                        js_patterns = ['window.', 'function', 'calendarComponentStates', 'true', 'false', 'null']
                        for pattern in js_patterns:
                            if pattern in word:
                                skip_word = True
                                break
                        if not skip_word and not re.match(r'^[{}[\],:"\\]*$', word):
                            cleaned_words.append(word)
                if cleaned_words:
                    cleaned_lines.append(' '.join(cleaned_words))
        # Rejoin lines with CR+LF to preserve line breaks
        cleaned_content = '\r\n'.join(cleaned_lines)
        print(f"Scraped content length: {len(cleaned_content)} characters")
    else:
        cleaned_content = ''

    # Prepare the final output (scraped content + untouched API data)
    output_content = cleaned_content
    if api_data is not None:
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"
        output_content += "=== API DATA: CoinMarketCap Fear & Greed Historical ===\r\n"
        output_content += "ENDPOINT: https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical\r\n"
        output_content += "=" * 60 + "\r\n\r\n"
        output_content += json.dumps(api_data, indent=2)
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    if not cleaned_content and api_data is None:
        print("Nothing to output.")
        return

    print("Content successfully extracted!")
    print("Preview (first 300 characters):")
    print("-" * 50)
    print(output_content[:300] + "..." if len(output_content) > 300 else output_content)
    print("-" * 50)
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cryptocraft_clean_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Multi-page scrape + API data collection\n")
        f.write(f"Pages scraped: {len(all_content)}\n")
        f.write(f"API endpoints: {len(enabled_apis)}\n")
        f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total length: {len(output_content)} characters\n")
        f.write("=" * 60 + "\n\n")
        f.write(output_content)

    print(f"Content saved to: {filename}")

if __name__ == "__main__":
    print("Starting cryptocraft scraper...")
    print("=" * 50)
    asyncio.run(scrape_and_save())
    print("Scraping complete!")