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
            
            # Get text content with structured line breaks
            print("Extracting content with structured formatting...")
            
            content = await page.evaluate('''
                () => {
                    // Remove script tags, style tags, and hidden elements
                    document.querySelectorAll('script, style, noscript, [style*="display:none"], [style*="display: none"]').forEach(el => el.remove());
                    
                    // Add line breaks for structural elements
                    const blockElements = document.querySelectorAll('div, p, tr, td, th, li, h1, h2, h3, h4, h5, h6, section, article, header, footer, nav');
                    blockElements.forEach(el => {
                        // Add newline before the element
                        const textNode = document.createTextNode('\\n');
                        if (el.parentNode) {
                            el.parentNode.insertBefore(textNode, el);
                        }
                    });
                    
                    // Special handling for table rows
                    document.querySelectorAll('tr').forEach(tr => {
                        const cells = tr.querySelectorAll('td, th');
                        cells.forEach((cell, index) => {
                            if (index > 0) {
                                // Add tab separator between cells
                                const tabNode = document.createTextNode('\\t');
                                cell.parentNode.insertBefore(tabNode, cell);
                            }
                        });
                        // Add double newline after each row
                        const newlineNode = document.createTextNode('\\n\\n');
                        if (tr.parentNode) {
                            tr.parentNode.insertBefore(newlineNode, tr.nextSibling);
                        }
                    });
                    
                    // Get the text content
                    return document.body.textContent || document.body.innerText || '';
                }
            ''')
            
            if content:
                # Clean up the content in Python
                import re
                
                # Remove JavaScript code patterns
                content = re.sub(r'window\.\w+\s*=\s*\{.*?\}', '', content, flags=re.DOTALL)
                content = re.sub(r'if\s*\([^)]*\)\s*\{.*?\}', '', content, flags=re.DOTALL)
                content = re.sub(r'\{[^}]*"[^"]*"[^}]*\}', '', content)
                
                # Remove JSON-like structures
                content = re.sub(r'\{[^}]*:[^}]*\}', '', content)
                content = re.sub(r'\[[^\]]*\]', '', content)
                
                # Remove HTML entities and artifacts
                content = re.sub(r'&[a-zA-Z0-9#]+;', ' ', content)
                content = re.sub(r'\\/', '/', content)
                content = re.sub(r'\\"', '"', content)
                content = re.sub(r'\\n', '\n', content)
                content = re.sub(r'\\t', '\t', content)
                
                # Clean up excessive whitespace but preserve line structure
                content = re.sub(r'[ ]+', ' ', content)  # Multiple spaces to single space
                content = re.sub(r'\n[ \t]*\n', '\n\n', content)  # Clean empty lines
                content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
                
                # Remove lines that are just JavaScript remnants
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    # Skip lines that look like JavaScript/JSON
                    if (line and 
                        not re.match(r'^[\{\}\[\],:"\\]*
            
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
, line) and
                        not re.match(r'^(true|false|null|\d+)
            
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
, line) and
                        not 'calendarComponentStates' in line and
                        not line.startswith('window.') and
                        len(line) > 3):
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines)
                content = content.strip()
            else:
                content = "No readable content found"
            
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
    