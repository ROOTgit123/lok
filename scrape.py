import os
import cloudscraper
import json
from datetime import datetime
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
URL = "https://temp-number.com/temporary-numbers/Canada/12262433061/1"
OUTPUT_DIR = "data"
# --------------------

def scrape_and_parse():
    """
    Scrapes the URL, saves the raw HTML, and then parses the content
    to save new messages to a JSON file.
    """
    print("Fetching HTML from the website...")
    try:
        # Use cloudscraper to bypass Cloudflare and get the real HTML
        scraper = cloudscraper.create_scraper()
        response = scraper.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        html_content = response.text
    except Exception as e:
        print(f"Error fetching page: {e}")
        return

    # Create the data directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- SAVE THE RAW HTML ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    html_filename = os.path.join(OUTPUT_DIR, f"canada_number_{timestamp}.html")
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully saved full HTML to {html_filename}")

    # --- PARSE THE HTML AND SAVE MESSAGES TO JSON ---
    print("\n[SCANNER] Checking for messages within the scraped HTML...")
    soup = BeautifulSoup(html_content, 'html.parser')
    messages = []
    
    # Find all message elements using the same CSS selector from your JavaScript
    message_elements = soup.find_all('div', class_='direct-chat-msg left')
    
    if not message_elements:
        print('[SCANNER] No messages found on this page.')
        return

    # Loop through each found message element and extract the data
    for msg_element in message_elements:
        sender_element = msg_element.find('span', class_='direct-chat-name')
        time_element = msg_element.find('span', class_='direct-chat-timestamp')
        text_element = msg_element.find('div', class_='direct-chat-text')

        # Check if all required elements exist before creating the message dictionary
        if sender_element and time_element and text_element:
            message_data = {
                'sender': sender_element.get_text(strip=True),
                'time': time_element.get_text(strip=True),
                'text': text_element.get_text(strip=True)
            }
            messages.append(message_data)

    # Save the list of messages to a JSON file
    if messages:
        json_filename = os.path.join(OUTPUT_DIR, f"messages_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            # The json.dump() function writes the Python list 'messages' to a file as a JSON array.
            json.dump(messages, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved {len(messages)} messages to {json_filename}")


# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    scrape_and_parse()
