import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def scrape_text_content(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print(f"Loading: {url}")
            await page.goto(url)
            await page.wait_for_timeout(5000)  # Wait for content to load
            
            print("Extracting text content...")
            
            # Get all text from the page
            page_text = await page.evaluate('''
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style, noscript');
                    scripts.forEach(el => el.remove());
                    
                    // Get text content and clean it up
                    const text = document.body.textContent || document.body.innerText || '';
                    
                    // Clean up whitespace and line breaks
                    return text
                        .replace(/\s+/g, ' ')  // Replace multiple spaces with single space
                        .replace(/\n\s*\n/g, '\n')  // Remove empty lines
                        .trim();
                }
            ''')
            
            print(f"\nText content length: {len(page_text)} characters")
            print("="*60)
            print("EXTRACTED TEXT CONTENT")
            print("="*60)
            print(page_text)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"text_content_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Text content from: {url}\n")
                f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                f.write(page_text)
            
            print(f"\n💾 Text saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await browser.close()

# Alternative function for structured text extraction
async def scrape_structured_text(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print(f"\nStructured extraction from: {url}")
            await page.goto(url)
            await page.wait_for_timeout(5000)
            
            # Extract different types of content
            content = {}
            
            # Get headings
            headings = await page.evaluate('''
                () => {
                    const h = [];
                    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(el => {
                        h.push(`${el.tagName}: ${el.textContent.trim()}`);
                    });
                    return h;
                }
            ''')
            
            # Get paragraphs
            paragraphs = await page.evaluate('''
                () => {
                    const p = [];
                    document.querySelectorAll('p').forEach(el => {
                        const text = el.textContent.trim();
                        if (text.length > 10) {  // Only include substantial paragraphs
                            p.push(text);
                        }
                    });
                    return p;
                }
            ''')
            
            # Get list items
            list_items = await page.evaluate('''
                () => {
                    const items = [];
                    document.querySelectorAll('li').forEach(el => {
                        const text = el.textContent.trim();
                        if (text && text.length > 5) {
                            items.push(text);
                        }
                    });
                    return items;
                }
            ''')
            
            # Display structured content
            print("\n" + "="*60)
            print("STRUCTURED TEXT CONTENT")
            print("="*60)
            
            if headings:
                print(f"\nHEADINGS ({len(headings)}):")
                for i, heading in enumerate(headings[:10], 1):  # Show first 10
                    print(f"{i:2d}. {heading}")
            
            if paragraphs:
                print(f"\nPARAGRAPHS ({len(paragraphs)}):")
                for i, para in enumerate(paragraphs[:5], 1):  # Show first 5
                    preview = para[:100] + "..." if len(para) > 100 else para
                    print(f"{i:2d}. {preview}")
            
            if list_items:
                print(f"\nLIST ITEMS ({len(list_items)}):")
                for i, item in enumerate(list_items[:10], 1):  # Show first 10
                    preview = item[:80] + "..." if len(item) > 80 else item
                    print(f"{i:2d}. {preview}")
            
            # Save structured content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"structured_text_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Structured text from: {url}\n")
                f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n")
                
                f.write(f"\nHEADINGS ({len(headings)}):\n")
                for i, heading in enumerate(headings, 1):
                    f.write(f"{i:2d}. {heading}\n")
                
                f.write(f"\nPARAGRAPHS ({len(paragraphs)}):\n")
                for i, para in enumerate(paragraphs, 1):
                    f.write(f"\n{i:2d}. {para}\n")
                
                if list_items:
                    f.write(f"\nLIST ITEMS ({len(list_items)}):\n")
                    for i, item in enumerate(list_items, 1):
                        f.write(f"{i:2d}. {item}\n")
            
            print(f"\n💾 Structured text saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await browser.close()

async def main():
    url = "https://www.cryptocraft.com/"
    
    print("🔍 Starting text extraction...")
    print("="*60)
    
    # Extract raw text content
    await scrape_text_content(url)
    
    # Extract structured text content
    await scrape_structured_text(url)
    
    print("\n✅ Text extraction complete!")

if __name__ == "__main__":
    asyncio.run(main())