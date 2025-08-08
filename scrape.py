import os
import json
from bs4 import BeautifulSoup
import re

# Define the input and output directories and filenames
input_dir = 'data'
output_dir = 'data'
input_filename = 'source.html'
output_json_filename = 'messages.json'
output_filtered_html_filename = 'filtered_messages.html'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def scrape_messages_from_html(file_path):
    """
    Reads an HTML file, finds the message container, and scrapes message data.
    Returns a list of message dictionaries.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        # Return a tuple of Nones to match the successful return signature
        return None, None

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main container for all messages
    messages_container = soup.find('div', class_='direct-chat-messages')

    if not messages_container:
        print("Could not find the main message container with class 'direct-chat-messages'.")
        return None, None

    messages_list = []
    
    # Find all individual message divs within the container
    message_elements = messages_container.find_all('div', class_='direct-chat-msg left')

    for message_element in message_elements:
        # Extract sender, timestamp, and message text
        sender_element = message_element.find('span', class_='direct-chat-name')
        timestamp_element = message_element.find('time', class_='direct-chat-timestamp')
        text_element = message_element.find('div', class_='direct-chat-text')
        
        sender = sender_element.get_text(strip=True) if sender_element else 'N/A'
        timestamp = timestamp_element.get_text(strip=True) if timestamp_element else 'N/A'
        
        # Get the full text, stripping unwanted elements like the button span
        message_text = ""
        if text_element:
            # Use .get_text() to get all text, then clean it up
            full_text = text_element.get_text(strip=True)
            # Remove the code snippets and extra spaces
            # This is a bit of a guess, as your example shows strong tags and numbers
            # A simple way to get a clean text is to get the children and join
            clean_text = ' '.join(part for part in text_element.stripped_strings)
            message_text = clean_text.strip()
        
        message_data = {
            'sender': sender,
            'timestamp': timestamp,
            'message': message_text
        }
        messages_list.append(message_data)
        
    return messages_list, messages_container.prettify()

def save_data_to_file(data, filename):
    """Saves the provided data to a file."""
    file_path = os.path.join(output_dir, filename)
    try:
        if filename.endswith('.json'):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(data)} messages to '{file_path}'.")
        elif filename.endswith('.html'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Successfully saved filtered HTML to '{file_path}'.")
        else:
            print("Unsupported file type. Please use .json or .html.")
    except IOError as e:
        print(f"Error: Could not save file '{file_path}'. {e}")

if __name__ == "__main__":
    # Construct the full path to the input HTML file
    input_file_path = os.path.join(input_dir, input_filename)
    
    # Scrape the data and filtered HTML
    scraped_messages, filtered_html_content = scrape_messages_from_html(input_file_path)
    
    if scraped_messages is not None:
        # Save the scraped messages to a JSON file
        save_data_to_file(scraped_messages, output_json_filename)
    
    if filtered_html_content is not None:
        # Save the filtered HTML content to a new file
        save_data_to_file(filtered_html_content, output_filtered_html_filename)
