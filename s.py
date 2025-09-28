import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re

async def scrape_and_save():
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
            url = "https://www.cryptocraft.com/"
            print(f"Accessing: {url}")
            print("Attempting to bypass Cloudflare...")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            print("Waiting for page to load completely...")
            await page.wait_for_timeout(8000)
            
            title = await page.title()
            print(f"Page title: {title}")
            
            # Extract content with proper line breaks
            print("Extracting and formatting content...")
            
            content = await page.evaluate('''
                () => {
                    // Remove scripts, styles, and hidden elements
                    document.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                    
                    // Get HTML content first to process table rows
                    let html = document.body.innerHTML || '';
                    
                    // Add newlines after </tr> tags - escape the regex properly
                    html = html.replace(/<\\/tr>/gi, '</tr>\\n');
                    
                    // Create a temporary div to extract text from modified HTML
                    let tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    let text = tempDiv.textContent || tempDiv.innerText || '';
                    
                    return text;
                }
            ''')
            
            if not content or len(content) < 100:
                print("Minimal content found, might be stuck on verification")
                
            # Clean up the content in Python
            print("Cleaning up content...")
            
            # Remove JavaScript patterns
            content = re.sub(r'window\.\w+\s*=\s*\{[^}]*\}', '', content)
            content = re.sub(r'if\s*\([^)]*\)\s*\{[^}]*\}', '', content)
            
            # Remove JSON-like patterns
            content = re.sub(r'\{[^}]*"[^"]*"[^}]*\}', '', content)
            content = re.sub(r'\[[^\]]*\]', '', content)
            
            # Clean whitespace
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            # Filter out JavaScript lines
            lines = content.split()
            cleaned_words = []
            
            for word in lines:
                word = word.strip()
                if word and len(word) > 1:
                    # Skip obvious JavaScript keywords and patterns
                    skip_word = False
                    js_patterns = ['window.', 'function', 'calendarComponentStates', 
                                 'true', 'false', 'null']
                    
                    for pattern in js_patterns:
                        if pattern in word:
                            skip_word = True
                            break
                    
                    # Skip words that are mostly punctuation
                    if not skip_word and not re.match(r'^[{}[\],:"\\]*$', word):
                        cleaned_words.append(word)
            
            # Rejoin words with spaces and create logical line breaks
            content = ' '.join(cleaned_words)
            
            print(f"Content length: {len(content)} characters")
            
            if len(content) < 50:
                print("Very minimal content - possibly verification page")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"verification_debug_{timestamp}.txt"
                
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Debug content from: {url}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content)
                
                print(f"Debug content saved to: {debug_filename}")
                
            else:
                print("Content successfully extracted!")
                print("Preview (first 300 characters):")
                print("-" * 50)
                print(content[:300] + "..." if len(content) > 300 else content)
                print("-" * 50)
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cryptocraft_clean_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Website: {url}\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(content)} characters\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(content)
                
                print(f"Content saved to: {filename}")
                
        except Exception as e:
            print(f"Error: {e}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_filename = f"error_{timestamp}.txt"
            
            with open(error_filename, 'w', encoding='utf-8') as f:
                f.write(f"ERROR REPORT\n")
                f.write(f"Website: {url}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {str(e)}\n")
            
            print(f"Error saved to: {error_filename}")
            
        finally:
            print("Closing browser...")
            await browser.close()

if __name__ == "__main__":
    print("Starting cryptocraft scraper...")
    print("=" * 50)
    asyncio.run(scrape_and_save())
    print("Scraping complete!")