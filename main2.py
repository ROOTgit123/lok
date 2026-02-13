import os
import time
import base64
import zipfile
import ast
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    return Driver(uc=True, headless=True, no_sandbox=True)

def generate_images(prompts, batch_num):
    driver = setup_driver()
    base_url = "https://duck.ai/chat?duckai=1"
    
    # Updated path to 'only' folder
    base_path = os.getcwd()
    only_repo_dir = os.path.join(base_path, "only")
    temp_raw = os.path.join(base_path, "temp_raw")
    
    os.makedirs(only_repo_dir, exist_ok=True)
    os.makedirs(temp_raw, exist_ok=True)
    
    raw_files = []

    try:
        for i, prompt in enumerate(prompts):
            print(f"--- Processing {i+1}/{len(prompts)} ---")
            driver.get(base_url)
            time.sleep(5)
            
            try:
                try: 
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
                except: pass
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
                
                textarea = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
                textarea.send_keys(prompt + Keys.ENTER)
                
                start_time = time.time()
                while time.time() - start_time < 120:
                    imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if imgs:
                        b64data = imgs[-1].get_attribute("src").split(",")[1]
                        raw_path = os.path.join(temp_raw, f"img_{i+1}.jpg")
                        with open(raw_path, "wb") as f:
                            f.write(base64.b64decode(b64data))
                        
                        if os.path.exists(raw_path):
                            raw_files.append(raw_path)
                            print(f"Captured Image {i+1}")
                        break
                    time.sleep(5)
            except Exception as e:
                print(f"Error on prompt {i+1}: {e}")

        if raw_files:
            # Saving to only/gen_X.zip
            z_path = os.path.join(only_repo_dir, f"gen_{batch_num}.zip")
            with zipfile.ZipFile(z_path, 'w') as z:
                for f in raw_files:
                    z.write(f, os.path.basename(f))
            print(f"Successfully Created: {z_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    raw_input = os.getenv("USER_PROMPTS", "").strip()
    manual_zip_num = os.getenv("ZIP_NUM", "1")
    
    if raw_input:
        try:
            list_data = raw_input.split("=", 1)[1].strip() if "=" in raw_input else raw_input
            my_prompts = ast.literal_eval(list_data)
            if isinstance(my_prompts, list):
                generate_images(my_prompts, manual_zip_num)
        except Exception as e:
            print(f"Parsing error: {e}")
