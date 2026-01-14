import os
import time
import base64
import zipfile
import cv2
import numpy as np
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- BACKGROUND REMOVAL LOGIC ---
def remove_background(image: np.ndarray, start_point: tuple, threshold: list) -> np.ndarray:
    if image.shape[2] == 4:
        img_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        img_bgr = image.copy()
    rows, cols = img_bgr.shape[:2]
    mask = np.zeros((rows + 2, cols + 2), np.uint8)
    flags = (8 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE)
    lo_diff = tuple(threshold)
    up_diff = tuple(threshold)
    cv2.floodFill(img_bgr, mask, start_point, newVal=(0, 0, 0), loDiff=lo_diff, upDiff=up_diff, flags=flags)
    result = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2BGRA)
    mask_cut = mask[1:-1, 1:-1]
    result[:, :, 3] = np.where(mask_cut == 1, 0, 255).astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    result[:, :, 3] = cv2.morphologyEx(result[:, :, 3], cv2.MORPH_OPEN, kernel)
    transparent = result[:, :, 3] == 0
    result[transparent, :3] = 0
    return result

# --- UTILS ---
def setup_driver():
    return Driver(uc=True, headless=True, no_sandbox=True)

def get_next_batch_number(dir1, dir2):
    os.makedirs(dir1, exist_ok=True)
    os.makedirs(dir2, exist_ok=True)
    i = 1
    while os.path.exists(os.path.join(dir1, f"gen_{i}.zip")) or os.path.exists(os.path.join(dir2, f"remove_{i}.zip")):
        i += 1
    return i

def save_base64_image(base64_str, filename, temp_dir):
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    if "," in base64_str: base64_str = base64_str.split(",")[1]
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(base64_str))
    return filepath

def generate_images(prompts):
    driver = setup_driver()
    base_url = "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1"
    
    images_repo_dir = os.path.join(os.getcwd(), "images")
    remove_repo_dir = os.path.join(os.getcwd(), "remove")
    temp_raw = os.path.join(os.getcwd(), "temp_raw")
    temp_no_bg = os.path.join(os.getcwd(), "temp_no_bg")
    
    batch_num = get_next_batch_number(images_repo_dir, remove_repo_dir)
    
    raw_files_list = []
    processed_files_list = []

    try:
        for i, prompt in enumerate(prompts):
            print(f"--- Processing {i+1}/{len(prompts)} ---")
            driver.get(base_url)
            time.sleep(5)
            try:
                # Agree & Mode Switch
                try: 
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
                except: pass
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
                
                # Input Prompt
                textarea = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
                textarea.send_keys(prompt + Keys.ENTER)
                
                # Wait for result
                start_time = time.time()
                while time.time() - start_time < 120:
                    imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if imgs:
                        # 1. Save Original
                        raw_name = f"img_{i+1}.jpg"
                        raw_path = save_base64_image(imgs[-1].get_attribute("src"), raw_name, temp_raw)
                        
                        # 2. Save Processed (No BG)
                        img_cv = cv2.imread(raw_path, cv2.IMREAD_UNCHANGED)
                        if img_cv is not None:
                            no_bg = remove_background(img_cv, (2,2), [200,200,200])
                            out_name = f"gen_{i+1}.png"
                            out_path = os.path.join(temp_no_bg, out_name)
                            cv2.imwrite(out_path, no_bg)
                            
                            # Verify they exist before adding to list
                            if os.path.exists(raw_path): raw_files_list.append(raw_path)
                            if os.path.exists(out_path): processed_files_list.append(out_path)
                            
                            print(f"Saved both raw and transparent for {i+1}")
                        break
                    time.sleep(5)
            except Exception as e:
                print(f"Error on {i+1}: {e}")

        # Final check on file existence before zipping
        raw_files_list = [f for f in raw_files_list if os.path.exists(f)]
        processed_files_list = [f for f in processed_files_list if os.path.exists(f)]

        # ZIP TRACK 1: ORIGINALS
        if raw_files_list:
            gen_zip_path = os.path.join(images_repo_dir, f"gen_{batch_num}.zip")
            with zipfile.ZipFile(gen_zip_path, 'w') as zipf:
                for file in raw_files_list:
                    zipf.write(file, os.path.basename(file))
            print(f"Created Original Zip: {gen_zip_path}")

        # ZIP TRACK 2: REMOVE BG
        if processed_files_list:
            rem_zip_path = os.path.join(remove_repo_dir, f"remove_{batch_num}.zip")
            with zipfile.ZipFile(rem_zip_path, 'w') as zipf:
                for file in processed_files_list:
                    zipf.write(file, os.path.basename(file))
            print(f"Created Background-Removed Zip: {rem_zip_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # Add your full list of prompts here
    my_prompts = [
        "Cute pixel art cat crying neon tears, white stroke, black background",
        "Cute pixel art puppy with neon eyes, white stroke, black background",
        "Cute pixel art fox emitting neon aura, white stroke, black background",
        "Cute pixel art bunny with neon pink ears, white stroke, black background"
    ]
    generate_images(my_prompts)
