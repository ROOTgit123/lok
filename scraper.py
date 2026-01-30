import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

# Configuration
LINKS_FILE = "links.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "roblox_codes_and_images.json")

def clean_game_name(title):
    """Cleans the H1 title to get a simple game name."""
    # Remove " codes", " January 2026", etc.
    name = re.sub(r'\s*codes.*', '', title, flags=re.IGNORECASE)
    return name.strip()

def clean_code(text):
    """
    Removes text after the first separator (e.g., ' - ', ' – ') and handles varied whitespace.
    This is the fix for the filtering issue.
    """
    # 1. Normalize all whitespace (including \u00a0) to a single space
    normalized_text = ' '.join(text.split())
    
    # 2. Use regex to find and split on the separator pattern: [whitespace][- or –][whitespace]
    match = re.search(r'\s*[-–]\s*', normalized_text)
    
    if match:
        # Split at the position of the match
        return normalized_text[:match.start()].strip()
    
    # Fallback: if no clear separator, return the normalized text
    return normalized_text.strip()

async def scrape_article(page, url):
    """Navigates to a single article and scrapes the game name, codes, and main image URL."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # --- 1. Extract Game Name ---
        h1_element = await page.locator('h1').first.inner_text()
        game_name = clean_game_name(h1_element)
        
        # --- 2. Extract Codes ---
        content_locator = page.locator('article, .entry-content, .article-content').first
        list_items = await content_locator.locator('ul li').all()
        
        codes_found = []
        for li in list_items:
            text = await li.inner_text()
            
            # Check if it looks like a code (contains bold/strong or a separator)
            is_bold = await li.locator('strong, b').count() > 0
            has_separator = ' - ' in text or ' – ' in text or '\u00a0-' in text
            
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

        # --- 3. Extract Main Image URL ---
        image_url = None
        
        # Try to find the first image within the main content
        image_locator = content_locator.locator('img').first
        
        if await image_locator.is_visible():
            image_url = await image_locator.get_attribute('src')
        
        # Fallback: If the first image is an ad or icon, try a figure image
        if not image_url or "logo" in image_url.lower() or "ad" in image_url.lower():
            figure_img_locator = content_locator.locator('figure img').first
            if await figure_img_locator.is_visible():
                image_url = await figure_img_locator.get_attribute('src')
        
        
        if game_name and (unique_codes or image_url):
            return {
                "game": game_name,
                "link": url,
                "codes": unique_codes,
                "image_url": image_url
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

    print(f"Starting combined scrape for {len(links)} articles...")
    
    scraped_data = []
    
    async with async_playwright() as p:
        # Use 'headless=True' for GitHub Actions environment
        browser = await p.chromium.launch(headless=True) 
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
