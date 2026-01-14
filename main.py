import os
import time
import base64
import zipfile
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    driver = Driver(uc=True, headless=True, no_sandbox=True)
    return driver

def get_next_zip_name(directory):
    """Finds the next available number for the zip file."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    i = 1
    while os.path.exists(os.path.join(directory, f"gen_{i}.zip")):
        i += 1
    return f"gen_{i}.zip"

def save_base64_image(base64_str, filename, temp_dir):
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(base64_str))
    return filepath

def generate_images(prompts):
    base_url = "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1"
    driver = setup_driver()
    
    repo_images_dir = os.path.join(os.getcwd(), "images")
    temp_folder = os.path.join(os.getcwd(), "temp_photos")
    
    saved_files = []

    try:
        for i, prompt in enumerate(prompts):
            print(f"--- Processing Image {i+1}/{len(prompts)} ---")
            driver.get(base_url)
            time.sleep(3)

            try:
                # Agree to terms
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
                # Switch to Image Mode
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
                time.sleep(2)
                
                # Input Prompt
                textarea = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
                textarea.send_keys(prompt + Keys.ENTER)
                
                # Wait for Image
                start_time = time.time()
                while time.time() - start_time < 100:
                    img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if img_elements:
                        path = save_base64_image(img_elements[-1].get_attribute("src"), f"img_{i+1}.jpg", temp_folder)
                        saved_files.append(path)
                        print(f"Captured image {i+1}")
                        break
                    time.sleep(5)
            except Exception as e:
                print(f"Error on prompt {i+1}: {e}")

        # ZIP LOGIC
        if saved_files:
            zip_filename = get_next_zip_name(repo_images_dir)
            zip_path = os.path.join(repo_images_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in saved_files:
                    zipf.write(file, os.path.basename(file))
                    os.remove(file) # Delete the loose jpg after zipping
            
            print(f"Successfully created: {zip_path}")
            if os.path.exists(temp_folder):
                os.rmdir(temp_folder)

    finally:
        driver.quit()

if __name__ == "__main__":
    my_prompts = [
        "Cute pixel art cat crying neon tears, white stroke, black background",
        "Cute pixel art puppy with neon eyes, white stroke, black background",
        "Cute pixel art fox emitting neon aura, white stroke, black background"
    ]
    generate_images(my_prompts)
