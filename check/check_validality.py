import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyautogui
import argparse
import logging
import time
import requests

def test_chrome_setup(url, base_dir):
    """Test if the URL is accessible and Chrome can render it."""
    print(f"Testing URL: {url}")

    # 1. Check HTTP status code first
    try:
        response = requests.get(url, timeout=20)
        if not response.ok:
            print(f"ERROR: URL returned status code {response.status_code}")
            return False
        print(f"✓ URL returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to {url}: {e}")
        return False

    # 2. Proceed with browser test if status is OK
    print("Testing Chrome setup...")
    
    # Check if Chrome binary exists
    chrome_path = "/opt/chrome-linux64/chrome"
    if not os.path.exists(chrome_path):
        print(f"ERROR: Chrome binary not found at {chrome_path}")
        return False
    
    # # Check if ChromeDriver exists
    chromedriver_path = "/usr/local/bin/chromedriver"
    if not os.path.exists(chromedriver_path):
        print(f"ERROR: ChromeDriver not found at {chromedriver_path}")
        return False
    
    print("✓ Chrome binary found")
    print("✓ ChromeDriver found")
    
    # Test Chrome startup
    try:
        chrome_options = Options()
        chrome_options.binary_location = chrome_path
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        driver.set_window_size(1920, 1080)
        time.sleep(2)
        screenshot = pyautogui.screenshot()

        # check the file num in /data/screenshots/
        screenshot_dir = "../data/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_files = os.listdir(screenshot_dir)
        items = base_dir.split("/")
        question_id, model_id = items[-2].strip(), items[-1].strip()
        screenshot_index = f"{question_id}_{model_id}"
        screenshot.save(f"{screenshot_dir}/{screenshot_index}.png")
        
        print(f"✓ Chrome started and rendered page successfully, screenshot saved to {screenshot_dir}/{screenshot_index}.png")
        
        driver.quit()
        print("✓ Chrome test completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Chrome test failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Chrome setup")
    parser.add_argument("--url", type=str, help="URL to test", required=True)
    parser.add_argument("--base_dir", type=str, help="Base ID", required=True)
    args = parser.parse_args()

    # Ensure URL has a scheme
    url_to_test = args.url
    if not url_to_test.startswith('http://') and not url_to_test.startswith('https://'):
        url_to_test = 'http://' + url_to_test

    success = test_chrome_setup(url_to_test, args.base_dir)
    if success:
        logging.info("Web test passed")
        sys.exit(0)
    else:
        logging.error("Web test failed")
        sys.exit(1)