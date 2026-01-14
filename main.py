import os
import time
import base64
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    # optimized for GitHub Actions (No GUI, bypasses bot detection)
    driver = Driver(uc=True, headless=True, no_sandbox=True)
    return driver

def save_base64_image(base64_str, filename, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Strip base64 metadata header
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
    
    # Set path to the 'images' folder in your repo
    image_dir = os.path.join(os.getcwd(), "images")

    try:
        driver.get(base_url)
        
        # Handle initial 'Agree' button
        try:
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))).click()
        except: pass

        # Ensure we are in Image Mode
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Image')]"))).click()
        except: pass

        for i, prompt in enumerate(prompts):
            print(f"Generating Image {i+1}...")
            textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            textarea.send_keys(prompt + Keys.ENTER)

            # Wait loop for the base64 image to render
            start_time = time.time()
            while time.time() - start_time < 90:
                try:
                    img = driver.find_element(By.XPATH, "//img[contains(@src, 'data:image')]")
                    if img.is_displayed():
                        # Save with a timestamp to avoid overwriting files
                        filename = f"gen_{int(time.time())}_{i+1}.jpg"
                        save_base64_image(img.get_attribute("src"), filename, image_dir)
                        break
                except: pass
                time.sleep(5)
            
            # Brief pause before next request
            time.sleep(2)

    finally:
        driver.quit()

if __name__ == "__main__":
    # Your prompt list
    my_prompts = [
        "Cute pixel art cat crying neon tears, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art puppy with neon glowing eyes, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art fox emitting neon aura, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art bunny with neon pink ears, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art baby bear holding a neon heart, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art owl with neon blue feathers, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art penguin with neon yellow bowtie, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art panda eating neon bamboo, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art squirrel with a neon glowing nut, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art bird with neon wings, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art mouse with neon cheese, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art otter floating with a neon stone, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art lamb with neon wool, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art piglet splashing in neon mud, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art hedgehog with neon spikes, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art baby dragon breathing neon fire, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art friendly monster with neon teeth, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art chibi character with neon sword, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art fairy with neon dust trail, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art sprite with neon leaf wings, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art kawaii creature with neon tentacles, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art star with neon twinkles, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art cloud raining neon drops, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art heart with a neon pulse, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art mushroom with neon spots, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art cupcake with neon frosting, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art strawberry with neon seeds, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art mini robot with neon circuits, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art cartoon character with neon glasses, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3",
"Cute pixel art blob monster with neon internal glow, glitch effect, script first desig same size with add whiite stroke to around design and keep black background --ar 2:3"
    ]
    generate_images(my_prompts)
