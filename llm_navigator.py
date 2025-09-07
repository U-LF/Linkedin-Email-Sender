import pyautogui
import pytesseract
from PIL import Image
import time
import logging
import sys

# ==============================
# Configurable constants
# ==============================
DEFAULT_CONFIDENCE = 0.8
DEFAULT_TIMEOUT = 10
BROWSER_ICON = "browser.png"
SEARCH_BAR_ICON = "search_bar.png"
QUERY_BOX_ICON = "query_box.png"

# Region for reading responses (x, y, width, height) – adjust for your screen
RESPONSE_REGION = (200, 200, 800, 600)

# ==============================
# Logging setup
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# Helper functions
# ==============================
def find_icon(icon_path, confidence=DEFAULT_CONFIDENCE):
    try:
        location = pyautogui.locateCenterOnScreen(icon_path, confidence=confidence)
        return (location.x, location.y) if location else None
    except Exception as e:
        logging.error(f"Error finding {icon_path}: {e}")
        return None

def click_icon(icon_path, confidence=DEFAULT_CONFIDENCE, timeout=DEFAULT_TIMEOUT):
    logging.info(f"Looking for {icon_path}...")
    start_time = time.time()
    wait_time = 0.5

    while time.time() - start_time < timeout:
        position = find_icon(icon_path, confidence)
        if position:
            pyautogui.click(position)
            logging.info(f"Clicked {icon_path} at {position}")
            return True
        time.sleep(wait_time)
        wait_time = min(wait_time * 1.5, 5)
    
    logging.error(f"Timeout: Could not find {icon_path}")
    return False

def focus_search_bar():
    if click_icon(SEARCH_BAR_ICON, timeout=5):
        return True
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1)
    return click_icon(SEARCH_BAR_ICON, timeout=2)

def open_browser_and_navigate():
    if not click_icon(BROWSER_ICON, timeout=15):
        logging.error("Browser icon not found.")
        return False
    
    time.sleep(3)
    if not focus_search_bar():
        return False
    
    pyautogui.write("chatgpt")
    pyautogui.press("enter")
    logging.info("Navigated to ChatGPT search results.")
    return True

def send_first_query(query):
    if not click_icon(QUERY_BOX_ICON, timeout=15):
        logging.error("Query box not found for first query.")
        return False
    pyautogui.write(query)
    pyautogui.press("enter")
    logging.info("First query sent.")
    return True

def send_next_query(query):
    # Assumes the chat input stays fixed after first query
    pyautogui.click(500, 950)  # Adjust coordinates for your chat input bar
    pyautogui.write(query)
    pyautogui.press("enter")
    logging.info("Subsequent query sent.")
    return True

def read_response():
    screenshot = pyautogui.screenshot(region=RESPONSE_REGION)
    text = pytesseract.image_to_string(screenshot)
    return text.strip()

# ==============================
# Main entry point
# ==============================
if __name__ == "__main__":
    logging.info("ChatGPT Automation Script")
    input("\nPress Enter to start...\n")
    
    if open_browser_and_navigate():
        logging.info("Waiting for ChatGPT to load...")
        time.sleep(10)
        
        if send_first_query("Hello ChatGPT, can you introduce yourself?"):
            logging.info("Waiting for response...")
            time.sleep(10)
            response = read_response()
            logging.info(f"First response captured:\n{response}")
            
            # Example subsequent query
            time.sleep(5)
            send_next_query("Can you explain AI in simple terms?")
            time.sleep(10)
            response2 = read_response()
            logging.info(f"Second response captured:\n{response2}")
    else:
        sys.exit(1)
