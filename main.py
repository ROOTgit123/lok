import os
import time
import base64
import random
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    # uc=True enables Undetected Chromedriver to bypass bot detection
    # headless=True is required for GitHub Actions
    driver = Driver(uc=True, headless=True)
    print("SeleniumBase Driver initialized successfully.")
    return driver

def save_base64_image(base64_str, filename, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Strip the header if present (e.g., "data:image/jpeg;base64,")
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    filepath = os.path.join(download_dir, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(base64_str))
        print(f"Successfully saved: {filename}")
        return True
    except Exception as e:
        print(f"Failed to save image: {e}")
    return False

def generate_images(prompts, base_dir):
    base_url = "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1"
    driver = setup_driver()

    # Define the upload directory
    image_dir = os.path.join(base_dir, "upload")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    try:
        print(f"Navigating to {base_url}...")
        driver.get(base_url)

        # 1. Click 'Agree and Continue'
        try:
            agree_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree and Continue')]"))
            )
            agree_btn.click()
            print("Clicked 'Agree and Continue'.")
        except Exception:
            print("Agree button not found; skipping.")

        # 2. Click 'New Image' mode
        print("Switching to 'New Image' mode...")
        try:
            # Try to find any button that indicates image creation
            img_mode_xpath = "//button[contains(., 'New Image') or contains(., 'Create Image')]"
            new_image_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, img_mode_xpath))
            )
            new_image_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"Could not find Image Mode button: {e}")

        for i, prompt in enumerate(prompts):
            print(f"\n--- Generating Image {i+1}/{len(prompts)} ---")
            
            try:
                # 3. Enter Prompt
                textarea = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
                textarea.clear()
                textarea.send_keys(prompt)
                textarea.send_keys(Keys.ENTER)
                print(f"Prompt sent: {prompt[:50]}...")

                # 4. Wait for image generation
                start_time = time.time()
                max_wait = 90 
                img_found = False

                while time.time() - start_time < max_wait:
                    try:
                        # DuckDuckGo embeds the result as a base64 string in the src attribute
                        img_element = driver.find_element(By.XPATH, "//img[contains(@src, 'data:image')]")
                        if img_element.is_displayed():
                            base64_data = img_element.get_attribute("src")
                            save_base64_image(base64_data, f"image_{i+1}.jpg", image_dir)
                            img_found = True
                            break
                    except:
                        pass
                    time.sleep(3)

                if not img_found:
                    print(f"Timed out waiting for image {i+1}")

                # 5. Reset for next prompt
                if i < len(prompts) - 1:
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)

            except Exception as e:
                print(f"Error during prompt {i+1}: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # In GitHub Actions, we use the current working directory
    current_workspace = os.getcwd()
    
    prompts = [
        "Cute pixel art cat crying neon tears, glitch effect, white stroke, black background",
        "Cute pixel art puppy with neon glowing eyes, glitch effect, white stroke, black background",
        "Cute pixel art fox emitting neon aura, glitch effect, white stroke, black background"
        # ... you can add the rest of your prompts here
    ]

    generate_images(prompts, current_workspace)
