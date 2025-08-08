import requests
import os
from datetime import datetime

# The URL to scrape
url = "https://temp-number.com/temporary-numbers/Canada/12262433061/1"

# Get the HTML content
response = requests.get(url)
html_content = response.text

# Create the data directory if it doesn't exist
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Generate a timestamped filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(output_dir, f"canada_number_{timestamp}.html")

# Save the HTML content to a file
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully scraped and saved HTML to {filename}")
