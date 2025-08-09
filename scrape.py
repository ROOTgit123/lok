import os
import cloudscraper
import json
from datetime import datetime
from bs4 import BeautifulSoup

url = "https://temp-number.com/temporary-numbers/Canada/12262433061/1"
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
html_content = response.text

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract phone number
phone_number = soup.select_one('.about__number-info a').text.strip()

# Extract all messages
messages = []
message_elements = soup.select('.direct-chat-msg.left')

for msg in message_elements:
    # Extract sender information
    sender_element = msg.select_one('.direct-chat-name')
    sender = sender_element.text.strip() if sender_element else "Unknown"
    
    # Extract timestamp
    time_element = msg.select_one('.timeago')
    timestamp = time_element.text.strip() if time_element else "Unknown time"
    
    # Extract message content
    text_element = msg.select_one('.direct-chat-text')
    message_text = text_element.text.strip() if text_element else "No message content"
    
    # Add to messages list
    messages.append({
        'sender': sender,
        'time': timestamp,
        'message': message_text
    })

# Create output directory if it doesn't exist
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Generate timestamp for filenames
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Save HTML file
html_filename = os.path.join(output_dir, f"canada_number_{timestamp}.html")
with open(html_filename, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"Successfully scraped and saved HTML to {html_filename}")

# Save JSON file with extracted data
json_filename = os.path.join(output_dir, f"canada_number_{timestamp}.json")
data = {
    'phone_number': phone_number,
    'scraped_at': datetime.now().isoformat(),
    'messages': messages
}
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"Successfully saved extracted data to {json_filename}")
