import os
import time
import base64
import ast
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# --- SETTINGS ---
BLOG_ID = "5968842906847838574"
OBD_CODE = os.getenv("OBD_CODE", "P0420").upper()
REPO = os.getenv("GITHUB_REPOSITORY", "ROOTgit123/lok")

def post_to_blogger_test():
    """Test function to post without Gemini API"""
    print(f"--- Running Blogger Test for {OBD_CODE} ---")
    
    # 1. Load Blogger Token
    token_raw = os.getenv("BLOGGER_TOKEN")
    if not token_raw:
        print("ERROR: BLOGGER_TOKEN secret is empty!")
        return

    try:
        token_data = ast.literal_eval(token_raw)
        creds = Credentials.from_authorized_user_info(token_data)
        service = build('blogger', 'v3', credentials=creds)
        
        # 2. Build the Image URLs from your GitHub Repo
        # This points to the images your script JUST pushed
        base_url = f"https://raw.githubusercontent.com/{REPO}/main/only/"
        
        test_content = f"""
        <div style="text-align:center;">
            <h1>Diagnostic Guide for {OBD_CODE}</h1>
            <img src="{base_url}{OBD_CODE}_main.jpg" style="max-width:100%; border-radius:10px;" alt="Main Image"/>
            <p>This is a test post to verify the automated system is working correctly.</p>
            
            <h3>Step 1: Initial Inspection</h3>
            <img src="{base_url}{OBD_CODE}_step1.jpg" style="max-width:80%;" alt="Step 1"/>
            
            <h3>Step 2: Component Testing</h3>
            <img src="{base_url}{OBD_CODE}_step2.jpg" style="max-width:80%;" alt="Step 2"/>
            
            <h3>Step 3: Final Repair</h3>
            <img src="{base_url}{OBD_CODE}_step3.jpg" style="max-width:80%;" alt="Step 3"/>
        </div>
        """

        body = {
            'kind': 'blogger#post',
            'title': f'TEST: {OBD_CODE} Automated Repair Post',
            'content': test_content,
            'labels': ['Test', OBD_CODE]
        }
        
        print(f"Uploading to Blog ID: {BLOG_ID}...")
        post = service.posts().insert(blogId=BLOG_ID, body=body).execute()
        print(f"SUCCESS! Check your blog: {post['url']}")

    except Exception as e:
        print(f"Blogger Upload Failed: {e}")

if __name__ == "__main__":
    # In this test, we assume images are already captured and pushed
    post_to_blogger_test()
