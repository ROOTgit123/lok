import os
import cloudscraper
import json
from datetime import datetime
from bs4 import BeautifulSoup
import sys
import re # We'll use a regular expression to reliably find the ID in the URL

def main():
    # Get URL from environment variable, with a fallback for local testing
    url = os.getenv("SCRAPE_URL", "https://temp-number.com/temporary-numbers/Canada/12262433061/1")
    print(f"Scraping URL: {url}")

    # Extract the phone number ID from the URL to use in the filename.
    # This regex finds the sequence of digits just before the final "/1" in the URL.
    match = re.search(r'/(\d+)/\d+$', url)
    if not match:
        print("Error: Could not extract phone number ID from the URL.")
        sys.exit(1)
    phone_id = match.group(1)
    print(f"Extracted Phone ID for filename: {phone_id}")

    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        html_content = response.text
        print("Successfully fetched HTML content.")

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract phone number (the full number displayed on the page)
        phone_number_element = soup.select_one('.about__number-info a')
        phone_number = phone_number_element.text.strip() if phone_number_element else "Not found"
        print(f"Found Phone Number: {phone_number}")

        # Extract all messages
        messages = []
        message_elements = soup.select('.direct-chat-msg.left')
        print(f"Found {len(message_elements)} messages.")

        for msg in message_elements:
            sender_element = msg.select_one('.direct-chat-name')
            sender = sender_element.text.strip() if sender_element else "Unknown"

            time_element = msg.select_one('.timeago')
            timestamp = time_element.text.strip() if time_element else "Unknown time"

            text_element = msg.select_one('.direct-chat-text')
            message_text = text_element.text.strip() if text_element else "No message content"

            messages.append({
                'sender': sender,
                'time': timestamp,
                'message': message_text
            })

        # --- File Saving Logic ---

        # Create output directory if it doesn't exist
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)

        # Define filenames based on the extracted phone ID
        html_filename = os.path.join(output_dir, f"{phone_id}.html")
        json_filename = os.path.join(output_dir, f"{phone_id}.json")

        # Save (overwrite) HTML file
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully saved/updated HTML to {html_filename}")

        # Save (overwrite) JSON file with extracted data
        data = {
            'phone_number': phone_number,
            'scraped_at': datetime.now().isoformat(),
            'url': url,
            'messages': messages
        }
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved/updated JSON to {json_filename}")

    except cloudscraper.exceptions.CloudflareException:
        print("Error: Cloudflare challenge failed. The site may have blocked the scraper.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
