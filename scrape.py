import os
import cloudscraper
from datetime import datetime
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
URL = "https://temp-number.com/temporary-numbers/Canada/12262433061/1"
OUTPUT_DIR = "data"
# --------------------

def scrape_and_parse():
    """
    Scrapes the URL, saves the raw HTML, and then parses the content
    to print new messages to the console.
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

    # Generate a timestamped filename and save the raw HTML content
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"canada_number_{timestamp}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully saved full HTML to {filename}")

    # --- PARSE THE HTML TO FIND MESSAGES ---
    print("\n[SCANNER] Checking for messages within the scraped HTML...")
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all message elements using the same CSS selector from your JavaScript
    message_elements = soup.find_all('div', class_='direct-chat-msg left')
    
    if not message_elements:
        print('[SCANNER] No messages found on this page.')
        return

    new_messages_found = 0
    # Loop through each found message element
    for msg_element in message_elements:
        # Extract the elements we need
        sender_element = msg_element.find('span', class_='direct-chat-name')
        time_element = msg_element.find('span', class_='direct-chat-timestamp')
        text_element = msg_element.find('div', class_='direct-chat-text')

        # Check if all required elements exist
        if sender_element and time_element and text_element:
            sender = sender_element.get_text(strip=True) if sender_element else 'N/A'
            message_time = time_element.get_text(strip=True) if time_element else 'N/A'
            message_text = text_element.get_text(strip=True) if text_element else 'N/A'

            # This part is a simple print, as we can't use localStorage in Python.
            # Each time the script runs, it will print all messages on the page.
            new_messages_found += 1
            print('---------------------')
            print(f'From: {sender}')
            print(f'Time: {message_time}')
            print(f'Text: "{message_text}"')
            print('---------------------')

    print(f"\n[SCANNER] Found and printed {new_messages_found} total messages from the page.")


# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    scrape_and_parse()
