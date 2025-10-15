import os
import time
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyautogui
import json
from evaluator.gui_agent import UITARS


CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"
ERROR_CODES = ["NONE RESPONSE", "PARSING RESPONSE ERROR", "UNRECOGNIZED ACTION TYPE", "SERVER ERROR", "INITIAL ERROR"]
WINDOW_SIZE = (1920, 1080)

INITIAL_WINDOW_POSITION = (0, 0)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

costs = {
    "prompt_token_count": 0,
    "candidates_token_count": 0,
    "thoughts_token_count": 0
}
codes = []

def setup_logger(name="AutoWebAgent"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[PID:%(process)d] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

# create a global logger
logger = setup_logger()


def initialize_environment(webpage_path):
    chrome_options = Options()
    chrome_options.binary_location = "/opt/chrome-linux64/chrome"
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

    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(webpage_path)
    driver.set_window_size(WINDOW_SIZE[0], WINDOW_SIZE[1])  # Set fixed size for consistency
    time.sleep(2)
    return driver

def capture_screenshot(screenshot_count, screenshot_dir):
    filename = f"screenshot_{screenshot_count:03d}.png"
    filepath = os.path.join(screenshot_dir, filename)
    
    # use pyautogui to capture the screenshot instead of selenium
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    logger.info(f"Save screenshot to: {filepath}")
    
    image_width, image_height = screenshot.size
    
    return filepath, image_width, image_height


def workflow(base_dir, instruction, host_url, task_type, max_steps):
    try:
        messages_path = os.path.join(base_dir, "messages.json")
        screenshot_dir = os.path.join(base_dir, "screenshots")
        logger.info("Initializing environment...")
        driver = initialize_environment(host_url)
        logger.info("Environment initialized successfully")
        
        screenshot_count = 1
        logger.info("Capturing initial screenshot...")
        image_path, image_width, image_height = capture_screenshot(screenshot_count, screenshot_dir)
        logger.info(f"Screenshot captured: {image_width}x{image_height}")
        
        vlm_agent = UITARS(use_thinking=False, max_steps=max_steps, task_type=task_type)
        messages = []
        
        while screenshot_count < max_steps:
            try:
                logger.info(f"Processing instruction (with screenshot {screenshot_count})...")
                pyautogui_code, messages, metadata = vlm_agent.predict(instruction=instruction, image_path=image_path, current_step=screenshot_count)
                screenshot_count += 1
                codes.append(pyautogui_code)
                image_path, image_width, image_height = capture_screenshot(screenshot_count, screenshot_dir)
                costs["prompt_token_count"] += metadata["prompt_token_count"]
                costs["candidates_token_count"] += metadata["candidates_token_count"]
                costs["thoughts_token_count"] += metadata["thoughts_token_count"]
            except Exception as e:
                logger.error(f"Error in workflow iteration (run_gui_agent.py): {e}")
                with open(messages_path, "w") as f:
                    json.dump({"final_result": "ERROR ITERATION", "error_message": str(e), "costs": costs, "trajectory": messages, "codes": codes}, f, indent=4, ensure_ascii=False)
                break
            if pyautogui_code == "DONE":
                logger.info("Workflow completed successfully")
                with open(messages_path, "w") as f:
                    json.dump({"final_result": "DONE", "costs": costs, "trajectory": messages, "codes": codes}, f, indent=4, ensure_ascii=False)
                break
            elif pyautogui_code == "FAILED":
                logger.info("Workflow completed with failed")
                with open(messages_path, "w") as f:
                    json.dump({"final_result": "FAILED", "costs": costs, "trajectory": messages, "codes": codes}, f, indent=4, ensure_ascii=False)
                break
            elif pyautogui_code in ERROR_CODES:
                logger.error(f"Workflow completed with error: {pyautogui_code}")
                with open(messages_path, "w") as f:
                    json.dump({"final_result": pyautogui_code, "costs": costs, "trajectory": messages, "codes": codes}, f, indent=4, ensure_ascii=False)
                break
            if screenshot_count == max_steps:
                logger.warning("reach the max number of screenshots")
                with open(messages_path, "w") as f:
                    json.dump({"final_result": "MAX ROUNDS", "error_message": "reach the max number of screenshots", "costs": costs, "trajectory": messages, "codes": codes}, f, indent=4, ensure_ascii=False)
                break
        driver.quit()
        logger.info("Workflow finished")
        
    except Exception as e:
        logger.error(f"Error in test_workflow:")
        logger.error(f"Error message: {str(e)}")
        with open(messages_path, "w") as f:
            json.dump({"final_result": "INITIAL_ERROR", "error_message": str(e), "costs": costs, "trajectory": None, "codes": codes}, f, indent=4, ensure_ascii=False)
        exit(0)

if __name__ == "__main__":
    # safe measures
    pyautogui.PAUSE = 1.0  # pause 1 second after each pyautogui operation
    pyautogui.FAILSAFE = True  # enable fail safe
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir", type=str, default="data/unit_test")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=str, default="3000")
    parser.add_argument("--webdev_unit", action="store_true")
    args = parser.parse_args()
    base_dir = args.base_dir
    host_url = f"http://{args.host}:{args.port}"
    if args.webdev_unit:
        host_url = f"file://{os.path.join(os.path.dirname(base_dir), 'web.html')}"
    
    with open(os.path.join(base_dir, "metadata.json"), "r") as f:
        metadata = json.load(f)
    instruction = metadata["instruction"]
    task_type = metadata["task_type"]
    max_steps = metadata["max_steps"]
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    if not os.path.exists(os.path.join(base_dir, "screenshots")):
        os.makedirs(os.path.join(base_dir, "screenshots"), exist_ok=True)
    
    logger.info("="*50)
    logger.info("Starting the workflow...")
    logger.info(f"messages will be saved to: {os.path.join(base_dir, 'messages.json')}")
    logger.info(f"screenshots will be saved to: {os.path.join(base_dir, 'screenshots')}")
    logger.info("="*50)
    workflow(base_dir, instruction, host_url, task_type, max_steps + 1)