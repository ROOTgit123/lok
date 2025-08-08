import os
import cloudscraper
from datetime import datetime

url = "https://temp-number.com/temporary-numbers/Canada/12262433061/1"

scraper = cloudscraper.create_scraper()
response = scraper.get(url)
html_content = response.text

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(output_dir, f"canada_number_{timestamp}.html")

with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully scraped and saved HTML to {filename}")
