import asyncio
from playwright.async_api import async_playwright

async def scrape_headless_stealth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # Keep headless
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
            print("Attempting to access site with stealth headers...")
            await page.goto("https://www.cryptocraft.com/", wait_until='domcontentloaded', timeout=60000)
            
            # Wait for potential Cloudflare check
            await page.wait_for_timeout(8000)
            
            # Check page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Try to get content
            content = await page.text_content('body')
            
            if "verifying" in content.lower():
                print("Still stuck on verification page")
                print("First 200 chars:", content[:200])
            else:
                print("Success! Got content:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(scrape_headless_stealth())