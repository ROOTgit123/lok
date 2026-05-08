import os
import time
import base64
import ast
import google.generativeai as genai
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# --- SETTINGS ---
GEMINI_KEY = os.getenv("GEMINI_KEY")
BLOG_ID = os.getenv("BLOG_ID")
OBD_CODE = os.getenv("OBD_CODE").upper()
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_image(prompt, filename):
    """Generates an image using DuckAI Selenium"""
    driver = Driver(uc=True, headless=True, no_sandbox=True)
    try:
        driver.get("https://duck.ai/chat?duckai=1")
        time.sleep(5)
        try: WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
        except: pass
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
        textarea = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
        textarea.send_keys(prompt + Keys.ENTER)
        
        time.sleep(40) # Wait for AI generation
        imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'data:image')]")
        if imgs:
            b64data = imgs[-1].get_attribute("src").split(",")[1]
            with open(f"only/{filename}", "wb") as f:
                f.write(base64.b64decode(b64data))
            print(f"Captured: {filename}")
    finally:
        driver.quit()

def write_article(code):
    """Uses Gemini to write a high-ranking SEO article"""
    prompt = f"""
    Act as a Master Auto Mechanic. Write a 1,500-word SEO-friendly repair guide for OBD2 code {code}.
    Format the entire response in HTML using <h2> and <h3> tags.
    
    Include these sections:
    1. Meaning of {code}.
    2. Common Symptoms.
    3. Step-by-Step Fix (Step 1, Step 2, Step 3).
    4. IMPORTANT: Place the text '[STEP_IMG]' on a new line after each step description.
    """
    response = model.generate_content(prompt)
    return response.text

def post_to_blogger(content):
    """Uploads the final HTML to Blogger"""
    token_data = ast.literal_eval(os.getenv("BLOGGER_TOKEN"))
    creds = Credentials.from_authorized_user_info(token_data)
    service = build('blogger', 'v3', credentials=creds)
    
    repo = os.getenv("GITHUB_REPOSITORY")
    # Base URL for Raw GitHub images
    base_url = f"https://raw.githubusercontent.com/{repo}/main/only/"
    
    # Insert Main Image at the Top
    final_html = f'<div style="text-align:center;"><img src="{base_url}{OBD_CODE}_main.jpg" style="max-width:100%; border-radius:10px;"/></div><br>' + content
    
    # Replace [STEP_IMG] with sequential step images
    for i in range(1, 4):
        img_tag = f'<div style="text-align:center;"><img src="{base_url}{OBD_CODE}_step{i}.jpg" style="max-width:90%;"/></div>'
        final_html = final_html.replace("[STEP_IMG]", img_tag, 1)

    body = {
        'kind': 'blogger#post',
        'title': f'How to Fix {OBD_CODE}: Diagnostic and Repair Guide',
        'content': final_html,
        'labels': [OBD_CODE, 'Repair Guide', 'OBD2']
    }
    
    service.posts().insert(blogId=BLOG_ID, body=body).execute()

if __name__ == "__main__":
    # Generate 4 distinct images
    get_image(f"Automotive engine part related to {OBD_CODE} high detail professional", f"{OBD_CODE}_main.jpg")
    get_image(f"Mechanic tools repairing {OBD_CODE} error", f"{OBD_CODE}_step1.jpg")
    get_image(f"Car engine diagnostic scanner showing {OBD_CODE}", f"{OBD_CODE}_step2.jpg")
    get_image(f"Hands fixing car engine component {OBD_CODE}", f"{OBD_CODE}_step3.jpg")
    
    # Generate Article and Post
    article_content = write_article(OBD_CODE)
    post_to_blogger(article_content)
