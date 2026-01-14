import os
import time
import base64
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
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
        print(f"Successfully saved to repository: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
    return False

def generate_images(prompts):
    base_url = "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1"
    driver = setup_driver()
    image_dir = os.path.join(os.getcwd(), "images")

    try:
        for i, prompt in enumerate(prompts):
            print(f"--- Processing Image {i+1}/{len(prompts)} ---")
            
            # Refresh page every time to reset the chat and clear any overlays
            driver.get(base_url)
            time.sleep(3)

            # 1. Handle 'Agree' button (if it appears)
            try:
                agree_xpath = "//button[contains(text(), 'Agree and Continue')]"
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, agree_xpath))).click()
            except:
                pass

            # 2. Switch to Image Mode
            try:
                img_mode_xpath = "//button[contains(., 'New Image') or contains(., 'Create Image')]"
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, img_mode_xpath))).click()
                time.sleep(2)
            except Exception as e:
                print(f"Note: Image mode button step skipped or failed: {e}")

            # 3. Find the visible textarea
            try:
                # Use a more specific selector for the active chat input
                textarea = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
                )
                textarea.click() # Click first to focus
                textarea.send_keys(prompt + Keys.ENTER)
                print(f"Prompt sent for image {i+1}")
            except Exception as e:
                print(f"Error finding textarea for image {i+1}: {e}")
                continue

            # 4. Wait loop for image
            start_time = time.time()
            img_found = False
            while time.time() - start_time < 100:
                try:
                    # Look for the image that contains base64 data
                    img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if img_elements:
                        # Take the last image generated in the chat
                        target_img = img_elements[-1]
                        if target_img.is_displayed():
                            filename = f"gen_{int(time.time())}_{i+1}.jpg"
                            save_base64_image(target_img.get_attribute("src"), filename, image_dir)
                            img_found = True
                            break
                except:
                    pass
                time.sleep(5)

            if not img_found:
                print(f"Timed out waiting for Image {i+1}")

    finally:
        driver.quit()

if __name__ == "__main__":
    my_prompts = [
        "Cute pixel art cat crying neon tears, white stroke, black background",
        "Cute pixel art puppy with neon eyes, white stroke, black background",
        "Cute pixel art fox emitting neon aura, white stroke, black background",
        "Cute pixel art bunny with neon pink ears, white stroke, black background"
    ]
    generate_images(my_prompts)
