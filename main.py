import os
import time
import base64
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    # optimized for GitHub Actions
    driver = Driver(uc=True, headless=True, no_sandbox=True)
    return driver

def save_base64_image(base64_str, filename, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    filepath = os.path.join(download_dir, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(base64_str))
        print(f"Saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
    return False

def generate_images(prompts):
    base_url = "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1"
    driver = setup_driver()
    
    # Path set specifically to 'images' folder in the repo
    image_dir = os.path.join(os.getcwd(), "images")

    try:
        driver.get(base_url)
        
        # Agree to Terms
        try:
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
        except: pass

        # Switch to Image Mode
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
        except: pass

        for i, prompt in enumerate(prompts):
            print(f"Processing: {prompt[:30]}...")
            textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            textarea.send_keys(prompt + Keys.ENTER)

            # Wait for image to appear
            start_time = time.time()
            while time.time() - start_time < 90:
                try:
                    img = driver.find_element(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if img.is_displayed():
                        save_base64_image(img.get_attribute("src"), f"gen_{i+1}_{int(time.time())}.jpg", image_dir)
                        break
                except: pass
                time.sleep(4)
            
            # Reset for next prompt
            driver.get(base_url) 
            time.sleep(2)

    finally:
        driver.quit()

if __name__ == "__main__":
    # Add your full list of prompts here
    my_prompts = [
        "Cute pixel art cat crying neon tears, white stroke, black background",
        "Cute pixel art puppy with neon eyes, white stroke, black background"
    ]
    generate_images(my_prompts)
