import sys
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta, timezone
import re
import aiohttp
import json
import csv

# ===============================
# Fear & Greed API (ISO output)
# ===============================
async def fetch_fear_greed_api():
    """
    Fetch Fear & Greed historical data (CoinMarketCap Pro).
    Returns a list of dicts with ISO timestamps.
    """
    api_key = "0ec32b61-d462-4be5-92f5-85d4f14ec474"  # <-- your key
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    txt = await resp.text()
                    print(f"[Fear&Greed] HTTP {resp.status}: {txt[:200]}")
                    return []
                raw = await resp.json()
                data = raw.get("data", [])
                out = []
                for d in data:
                    try:
                        ts = int(d["timestamp"])
                        iso = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")
                        out.append({
                            "timestamp": iso,
                            "value": d.get("value"),
                            "value_classification": d.get("value_classification")
                        })
                    except Exception:
                        continue
                return out
    except Exception as e:
        print(f"[Fear&Greed] Error: {e}")
        return []

# ===============================
# Whale Alert text parser (ISO)
# ===============================
def parse_whale_alerts(scraped_text: str):
    """
    Parse the visible text of whale-alert.io/alerts.html into structured events.
    Expects the same plain text format your scraper outputs.
    """
    alerts = []
    if not scraped_text:
        return alerts

    lines = [ln.strip() for ln in scraped_text.splitlines() if ln.strip()]
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    i = 0
    while i < len(lines) - 2:
        line = lines[i]

        # Absolute timestamp: "27-Sept-2025 19:59"
        m_abs = re.match(r"(\d{1,2})-([A-Za-z]+)-(\d{4}) (\d{2}):(\d{2})", line)
        if m_abs:
            try:
                day = int(m_abs.group(1))
                mon_str = m_abs.group(2)
                year = int(m_abs.group(3))
                hour = int(m_abs.group(4))
                minute = int(m_abs.group(5))
                month = months.get(mon_str[:3], 1)
                dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
                ts_iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                ts_iso = None

            amount_line = lines[i+1] if i+1 < len(lines) else ""
            desc_line = lines[i+2] if i+2 < len(lines) else ""
            alerts.append(_parse_single_alert(amount_line, desc_line, ts_iso))
            i += 3
            continue

        # Relative timestamp: "45 mins ago", "3 hours ago"
        m_rel = re.match(r"(\d+)\s+(mins?|hours?|days?) ago", line, re.IGNORECASE)
        if m_rel:
            qty = int(m_rel.group(1))
            unit = m_rel.group(2).lower()
            now = datetime.now(timezone.utc)
            if "min" in unit:
                dt = now - timedelta(minutes=qty)
            elif "hour" in unit:
                dt = now - timedelta(hours=qty)
            elif "day" in unit:
                dt = now - timedelta(days=qty)
            else:
                dt = now
            ts_iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            amount_line = lines[i+1] if i+1 < len(lines) else ""
            desc_line = lines[i+2] if i+2 < len(lines) else ""
            alerts.append(_parse_single_alert(amount_line, desc_line, ts_iso))
            i += 3
            continue

        i += 1

    # Drop Nones or empties
    alerts = [a for a in alerts if a.get("asset") or a.get("usd_value")]
    return alerts

def _parse_single_alert(amount_line: str, desc_line: str, timestamp_iso: str):
    # Amount line example: "400 #BTC (44,322,294 USD)"
    m = re.match(r"([\d,\.]+)\s+#([A-Z0-9]+)\s+\(([\d,\.]+)\s+USD\)", amount_line)
    amount = float(m.group(1).replace(",", "")) if m else None
    asset = m.group(2) if m else None
    usd_value = float(m.group(3).replace(",", "")) if m else None

    event = "transfer"
    src = None
    dst = None
    extra = None

    d = desc_line.lower()
    if "transferred" in d:
        event = "transfer"
        md = re.match(r"transferred from (.+) to (.+)", desc_line, re.IGNORECASE)
        if md:
            src = md.group(1)
            dst = md.group(2)
    elif "minted" in d:
        event = "mint"
        md = re.match(r"minted at (.+)", desc_line, re.IGNORECASE)
        if md:
            dst = md.group(1)
    elif "burned" in d:
        event = "burn"
        md = re.match(r"burned at (.+)", desc_line, re.IGNORECASE)
        if md:
            src = md.group(1)
    elif "activated" in d:
        event = "dormant_activation"
        md = re.match(r".*after ([\d\.]+) years", desc_line, re.IGNORECASE)
        if md:
            extra = {"age_years": float(md.group(1))}

    return {
        "timestamp": timestamp_iso,
        "event": event,
        "asset": asset,
        "amount": amount,
        "usd_value": usd_value,
        "from": src,
        "to": dst,
        "extra": extra
    }

# ===============================
# Post-processor helpers (NEW)
# ===============================
EXCHANGE_KEYWORDS = {
    "binance","coinbase","coinbase institutional","kraken","bitfinex","okx","okex",
    "ceffu","gemini","aave","htx","cumberland","antpool","falconx","bitwise","bitwise etf"
}

def parse_iso(ts: str) -> datetime:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts.replace("Z","+00:00"))
        return datetime.fromisoformat(ts)
    except Exception:
        # epoch fallback
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except Exception:
            return None

def is_exchange(name):
    if not name:
        return False
    s = str(name).strip().lower().lstrip("#")
    return any(kw in s for kw in EXCHANGE_KEYWORDS)

def tag_alert(alert):
    ev = (alert.get("event") or "").lower()
    if ev in {"mint","burn","lock/freeze","unlock/unfreeze"}:
        return "neutral"
    to = alert.get("to")
    fr = alert.get("from")
    if is_exchange(to):
        return "inflow"
    if is_exchange(fr):
        return "outflow"
    return "neutral"

def summarize_sentiment(fg_points):
    pts = []
    for p in fg_points or []:
        dt = parse_iso(str(p.get("timestamp")))
        if not dt:
            continue
        pts.append((dt, int(p.get("value")), p.get("value_classification")))
    pts.sort(key=lambda x: x[0])
    if not pts:
        return {"latest": None}
    latest_dt, latest_val, latest_class = pts[-1]
    prev_val = pts[-2][1] if len(pts) > 1 else None
    delta = latest_val - prev_val if prev_val is not None else None
    trend_7d = latest_val - pts[-7][1] if len(pts) >= 7 else None
    return {
        "latest_time": latest_dt.isoformat(),
        "latest": latest_val,
        "latest_class": latest_class,
        "delta_vs_prev": delta,
        "delta_vs_7d": trend_7d
    }

def summarize_flows(wa, hours: int):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=hours)
    inflow_btc = 0.0
    outflow_btc = 0.0
    tagged_rows = []

    for a in wa or []:
        ts = parse_iso(str(a.get("timestamp")))
        if not ts or ts < window_start:
            continue
        asset = (a.get("asset") or "").upper()
        tag = tag_alert(a)
        amt = float(a.get("amount") or 0.0)
        tagged_rows.append({
            "timestamp": ts.isoformat(),
            "event": a.get("event"),
            "asset": asset,
            "amount": amt,
            "usd_value": a.get("usd_value"),
            "from": a.get("from"),
            "to": a.get("to"),
            "tag": tag
        })
        if asset == "BTC":
            if tag == "inflow":
                inflow_btc += amt
            elif tag == "outflow":
                outflow_btc += amt

    return {
        "window_hours": hours,
        "from": window_start.isoformat(),
        "to": now.isoformat(),
        "btc_inflows": inflow_btc,
        "btc_outflows": outflow_btc,
        "btc_net": outflow_btc - inflow_btc,
        "tagged": tagged_rows
    }

def write_csv(path, rows):
    if not path or not rows:
        return
    fields = ["timestamp","event","asset","amount","usd_value","from","to","tag"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})

def parse_optional_flags(argv):
    hours = 24
    csv_path = None
    for arg in argv:
        if arg.startswith("--hours="):
            try:
                hours = int(arg.split("=",1)[1])
            except Exception:
                pass
        elif arg.startswith("--csv="):
            csv_path = arg.split("=",1)[1]
    return hours, csv_path

# ===============================
# Your original scraper + exports
# ===============================
async def scrape_and_save():
    # ---- DO NOT TOUCH: scraping URLs / mapping ----
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
    # -----------------------------------------------

    # Parse CLI args for enabled sites/APIs
    enabled_sites = set()
    enabled_apis = set()
    for arg in sys.argv[1:]:
        if arg in site_map:
            enabled_sites.add(arg)
        if arg in api_map:
            enabled_apis.add(arg)
    hours, csv_path = parse_optional_flags(sys.argv[1:])

    if not enabled_sites and not enabled_apis:
        print("No sites or APIs selected. Usage:")
        print("  python s.py [cc_home] [cc_btc] [cc_news] [cmc_chart] [whale_alert] [fear_api] [--hours=24] [--csv=out.csv]")
        print("  Example: python s.py cc_home cc_btc whale_alert fear_api --hours=24 --csv=whale_alerts_tagged.csv")
        print("  Available:")
        for k, v in site_map.items():
            print(f"    {k}: {v['desc']}")
        for k, v in api_map.items():
            print(f"    {k}: {v['desc']}")
        return

    # ================
    # Scrape pages
    # ================
    all_content = []
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
                        'key': key,
                        'url': url,
                        'title': title,
                        'content': content
                    }
                    all_content.append(page_info)
                    print(f"Content extracted from {url} - Length: {len(content)} characters")
            finally:
                print("Closing browser...")
                await browser.close()

    # ==========================
    # Fetch Fear & Greed (API)
    # ==========================
    api_data = None
    if 'fear_api' in enabled_apis:
        print("Fetching Fear and Greed historical data from API...")
        fear_greed_list = await api_map['fear_api']['func']()
        api_data = {
            "data": fear_greed_list,
            "status": {
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "CoinMarketCap Fear & Greed / v3"
            }
        }

    # ==========================
    # Build cleaned text output
    # ==========================
    scraped_content = ""
    for page in all_content:
        scraped_content += f"=== PAGE: {page['url']} ===\r\n"
        scraped_content += f"TITLE: {page['title']}\r\n"
        scraped_content += "=" * 60 + "\r\n\r\n"
        scraped_content += page['content']
        scraped_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    # Clean visible text
    if scraped_content:
        print("Cleaning up scraped content...")
        content = scraped_content
        content = re.sub(r'window\.\w+\s*=\s*\{[^}]*\}', '', content)
        content = re.sub(r'if\s*\([^)]*\)\s*\{[^}]*\}', '', content)
        content = re.sub(r'\{[^}]*"[^"]*"[^}]*\}', '', content)
        content = re.sub(r'\[[^\]]*\]', '', content)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'[ \t]+', ' ', line.strip())
            if line:
                words = line.split()
                cleaned_words = []
                for word in words:
                    if word and len(word) > 1:
                        skip = False
                        for pattern in ['window.', 'function', 'calendarComponentStates', 'true', 'false', 'null']:
                            if pattern in word:
                                skip = True
                                break
                        if not skip and not re.match(r'^[{}[\],:"\\]*$', word):
                            cleaned_words.append(word)
                if cleaned_words:
                    cleaned_lines.append(' '.join(cleaned_words))
        cleaned_content = '\r\n'.join(cleaned_lines)
        print(f"Scraped content length: {len(cleaned_content)} characters")
    else:
        cleaned_content = ''

    # ==========================================
    # Append JSON sections to the text output
    # ==========================================
    output_content = cleaned_content

    # Parse Whale Alerts from the scraped Whale page (if present)
    whale_text = ""
    for page in all_content:
        if "whale-alert.io/alerts.html" in page["url"]:
            whale_text = page["content"]
            break
    whale_alerts = parse_whale_alerts(whale_text) if whale_text else []

    # Append Fear & Greed JSON (if fetched)
    if api_data is not None:
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"
        output_content += "=== API DATA: CoinMarketCap Fear & Greed (ISO timestamps) ===\r\n"
        output_content += "=" * 60 + "\r\n\r\n"
        output_content += json.dumps(api_data, indent=2)
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    # Append Whale Alerts JSON (parsed)
    if whale_alerts:
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"
        output_content += "=== PARSED Whale Alerts (JSON) ===\r\n"
        output_content += "=" * 60 + "\r\n\r\n"
        output_content += json.dumps({"alerts": whale_alerts}, indent=2)
        output_content += "\r\n\r\n" + "=" * 60 + "\r\n\r\n"

    if not cleaned_content and api_data is None and not whale_alerts:
        print("Nothing to output.")
        return

    # ==========================
    # Save text file
    # ==========================
    print("Content successfully extracted!")
    print("Preview (first 300 characters):")
    print("-" * 50)
    print(output_content[:300] + "..." if len(output_content) > 300 else output_content)
    print("-" * 50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cryptocraft_clean_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Multi-page scrape + API data collection\n")
        f.write(f"Pages scraped: {len(all_content)}\n")
        f.write(f"API endpoints: {len(enabled_apis)}\n")
        f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total length: {len(output_content)} characters\n")
        f.write("=" * 60 + "\n\n")
        f.write(output_content)
    print(f"Content saved to: {filename}")

    # ==========================
    # Save structured JSON file
    # ==========================
    structured = {
        "fear_greed": api_data["data"] if api_data else [],
        "whale_alerts": whale_alerts,
        "meta": {
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    json_filename = f"crypto_structured_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(structured, jf, indent=2)
    print(f"Structured JSON saved to: {json_filename}")

    # ==========================
    # Post-process summary (NEW)
    # ==========================
    print("="*70)
    print("POST-PROCESS SUMMARY")
    sent = summarize_sentiment(structured["fear_greed"])
    flows = summarize_flows(structured["whale_alerts"], hours)

    print("BTC FLOW SUMMARY")
    print(f"- Window:     last {flows['window_hours']} hours")
    print(f"- Time range: {flows['from']}  →  {flows['to']}")
    print(f"- BTC inflows to exchanges:     {flows['btc_inflows']:,.2f} BTC")
    print(f"- BTC outflows from exchanges:  {flows['btc_outflows']:,.2f} BTC")
    net = flows['btc_net']
    print(f"- BTC NET (out - in):           {net:,.2f} BTC")
    bias = "ACCUMULATION (withdrawals dominate)" if net > 0 else ("DISTRIBUTION (inflows dominate)" if net < 0 else "NEUTRAL")
    print(f"- Flow bias: {bias}")
    print("-"*70)
    print("SENTIMENT (Fear & Greed)")
    if sent.get("latest") is None:
        print("- No sentiment points found")
    else:
        print(f"- Latest: {sent['latest']} ({sent['latest_class']}) at {sent['latest_time']}")
        if sent.get("delta_vs_prev") is not None:
            print(f"- Δ vs prev: {sent['delta_vs_prev']:+d}")
        if sent.get("delta_vs_7d") is not None:
            print(f"- Δ vs 7d:   {sent['delta_vs_7d']:+d}")
    print("="*70)

    if csv_path:
        try:
            write_csv(csv_path, flows["tagged"])
            print(f"Wrote tagged alerts CSV → {csv_path}")
        except Exception as e:
            print(f"Failed to write CSV: {e}")

if __name__ == "__main__":
    print("Starting cryptocraft scraper...")
    print("=" * 50)
    asyncio.run(scrape_and_save())
    print("Scraping complete!")
