import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def scrape_and_save():
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
            url = "https://www.cryptocraft.com/"
            print(f"Accessing: {url}")
            print("Attempting to bypass Cloudflare...")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for potential Cloudflare check
            print("Waiting for page to load completely...")
            await page.wait_for_timeout(8000)
            
            # Check page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Get text content using a simpler approach
            content = await page.text_content('body')
            
            if content:
                # Clean up the content in Python instead of JavaScript
                import re
                content = re.sub(r'\s+', ' ', content)  # Replace multiple whitespace with single space
                content = re.sub(r'\n\s*\n', '\n', content)  # Remove multiple empty lines
                content = content.strip()
            else:
                content = "No content found"
            
            print(f"Content length: {len(content)} characters")
            
            if "verifying" in content.lower() or len(content) < 100:
                print("❌ Still stuck on verification page or minimal content")
                print("First 200 chars:", content[:200])
                
                # Save the verification page content too for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"verification_page_{timestamp}.txt"
                
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Verification page content from: {url}\n")
                    f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    f.write(content)
                
                print(f"🔍 Debug content saved to: {debug_filename}")
                
            else:
                print("✅ Successfully retrieved content!")
                print("Preview (first 300 chars):")
                print("-" * 50)
                print(content[:300] + "..." if len(content) > 300 else content)
                print("-" * 50)
                
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cryptocraft_content_{timestamp}.txt"
                
                # Write content to file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Website: {url}\n")
                    f.write(f"Page Title: {title}\n")
                    f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Content length: {len(content)} characters\n")
                    f.write("="*60 + "\n\n")
                    f.write(content)
                
                print(f"💾 Content saved to: {filename}")
                
                # Also create a summary file with key statistics
                summary_filename = f"cryptocraft_summary_{timestamp}.txt"
                
                # Extract some basic stats
                word_count = len(content.split())
                line_count = len(content.split('\n'))
                
                with open(summary_filename, 'w', encoding='utf-8') as f:
                    f.write(f"SCRAPING SUMMARY\n")
                    f.write(f"Website: {url}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Page Title: {title}\n")
                    f.write(f"Character count: {len(content):,}\n")
                    f.write(f"Word count: {word_count:,}\n")
                    f.write(f"Line count: {line_count:,}\n")
                    f.write(f"Main content file: {filename}\n")
                    f.write("="*60 + "\n\n")
                    f.write("PREVIEW (first 500 characters):\n")
                    f.write(content[:500])
                    if len(content) > 500:
                        f.write("\n\n... (truncated, see main file for full content)")
                
                print(f"📊 Summary saved to: {summary_filename}")
                
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            
            # Save error info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_filename = f"scraping_error_{timestamp}.txt"
            
            with open(error_filename, 'w', encoding='utf-8') as f:
                f.write(f"SCRAPING ERROR\n")
                f.write(f"Website: https://www.cryptocraft.com/\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {str(e)}\n")
            
            print(f"❌ Error details saved to: {error_filename}")
            
        finally:
            print("Closing browser...")
            await browser.close()

# Run the scraper
if __name__ == "__main__":
    print("🚀 Starting Cryptocraft.com text scraper...")
    print("="*60)
    asyncio.run(scrape_and_save())
    print("\n✅ Scraping complete!")
    print("📁 Check the generated .txt files for results")