import asyncio
from playwright.async_api import async_playwright

async def scrape_with_headers():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Try non-headless first
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        page = await context.new_page()
        
        try:
            print("Loading page with browser headers...")
            await page.goto("https://www.cryptocraft.com/", wait_until='networkidle', timeout=30000)
            
            # Wait longer for Cloudflare check
            print("Waiting for Cloudflare verification...")
            await page.wait_for_timeout(10000)  # Wait 10 seconds
            
            # Check if we're past the verification
            title = await page.title()
            print(f"Page title: {title}")
            
            if "verifying" in title.lower() or "checking" in title.lower():
                print("Still in verification, waiting longer...")
                await page.wait_for_timeout(15000)  # Wait another 15 seconds
            
            # Now try to get content
            content = await page.text_content('body')
            print(content[:500] + "..." if len(content) > 500 else content)
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(scrape_with_headers())