import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

# Configuration
LINKS_FILE = "links.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "roblox_codes.json")

def clean_game_name(title):
    """Cleans the H1 title to get a simple game name."""
    # Remove " codes", " January 2026", etc.
    name = re.sub(r'\s*codes.*', '', title, flags=re.IGNORECASE)
    return name.strip()

def clean_code(text):
    """Removes text after the first '-' or '–' separator."""
    if ' - ' in text:
        return text.split(' - ')[0].strip()
    if ' – ' in text:
        return text.split(' – ')[0].strip()
    return text.strip()

async def scrape_article(page, url):
    """Navigates to a single article and scrapes the game name and codes."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 1. Extract Game Name
        h1_element = await page.locator('h1').first.inner_text()
        game_name = clean_game_name(h1_element)
        
        # 2. Extract Codes
        # Target the main content area to avoid sidebar/footer lists
        content_locator = page.locator('article, .entry-content, .article-content').first
        
        # Find all <li> elements within <ul> tags in the content area
        list_items = await content_locator.locator('ul li').all()
        
        codes_found = []
        for li in list_items:
            text = await li.inner_text()
            
            # Check if it looks like a code (contains bold/strong or a separator)
            is_bold = await li.locator('strong, b').count() > 0
            has_separator = ' - ' in text or ' – ' in text
            
            if text and (is_bold or has_separator):
                cleaned_code = clean_code(text)
                
                # Basic validation to filter out noise
                lower_code = cleaned_code.lower()
                if cleaned_code and len(cleaned_code) > 1 and \
                   not lower_code.startswith('click here') and \
                   not lower_code.startswith('how to') and \
                   not lower_code.startswith('follow us'):
                    codes_found.append(cleaned_code)

        # Remove duplicates
        unique_codes = list(set(codes_found))
        
        if game_name and unique_codes:
            return {
                "game": game_name,
                "link": url,
                "codes": unique_codes
            }
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

async def main():
    # Read links from file
    if not os.path.exists(LINKS_FILE):
        print(f"Error: {LINKS_FILE} not found.")
        return

    with open(LINKS_FILE, 'r') as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("No links found in links.txt. Exiting.")
        return

    print(f"Starting scrape for {len(links)} articles...")
    
    scraped_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        for i, url in enumerate(links):
            print(f"[{i+1}/{len(links)}] Scraping: {url}")
            result = await scrape_article(page, url)
            if result:
                scraped_data.append(result)
        
        await browser.close()

    # Safety Check and Save
    if not scraped_data:
        print("Warning: Scraped data is empty. Preserving existing data file (if any).")
        return

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(scraped_data, f, indent=4)
    
    print(f"Successfully scraped {len(scraped_data)} games and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
