import pyautogui
import time
import logging
import sys

# ==============================
# Configurable constants
# ==============================
DEFAULT_CONFIDENCE = 0.8   # Confidence threshold for image matching
DEFAULT_TIMEOUT = 10       # Timeout in seconds for waiting
BROWSER_ICON = "browser.png"
SEARCH_BAR_ICON = "search_bar.png"
COMPOSE_ICON = "compose.png"
TO_ICON = "to.png"
SUBJECT_ICON = "subject.png"
EMAIL_ICON = "email.png"
SEND_ICON = "send.png"

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

# ==============================
# Gmail Automation
# ==============================
def compose_and_send_email():
    """
    Automate composing and sending an email in Gmail.
    """
    # Step 1: Click compose button
    if not click_icon(COMPOSE_ICON, timeout=15):
        return False
    time.sleep(2)

    # Step 2: Enter recipient email
    if click_icon(TO_ICON, timeout=10):
        pyautogui.write("dummyemail@example.com")
        pyautogui.press("tab")  # move to subject
        time.sleep(1)
    else:
        return False

    # Step 3: Enter subject
    if click_icon(SUBJECT_ICON, timeout=10):
        pyautogui.write("Test Subject from Automation")
        pyautogui.press("tab")  # move to body
        time.sleep(1)
    else:
        return False

    # Step 4: Enter email body
    if click_icon(EMAIL_ICON, timeout=10):
        pyautogui.write("Hello,\n\nThis is a test email sent by Linkedin email automation script.\n\nBest,\nAutomation Script")
        time.sleep(1)
    else:
        return False

    # Step 5: Click send
    if not click_icon(SEND_ICON, timeout=10):
        return False
    
    logging.info("Email composed and sent successfully!")
    return True

# ==============================
# Core automation
# ==============================
def focus_search_bar():
    if click_icon(SEARCH_BAR_ICON, timeout=5):
        return True
    
    logging.warning("Search bar not found. Trying alternative approaches...")
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1)
    
    if click_icon(SEARCH_BAR_ICON, timeout=2):
        return True
    
    logging.info("Opening a new tab...")
    pyautogui.hotkey("ctrl", "t")
    time.sleep(2)
    
    if click_icon(SEARCH_BAR_ICON, timeout=5):
        return True
    
    logging.error("Could not find search bar even after opening a new tab.")
    return False

def focus_window():
    screen_w, screen_h = pyautogui.size()
    center_x, center_y = screen_w // 2, screen_h // 2
    pyautogui.click(center_x, center_y)
    logging.info(f"Clicked center of the screen at ({center_x}, {center_y}) to focus window.")
    time.sleep(1)

def open_browser_and_navigate():
    if not click_icon(BROWSER_ICON, timeout=15):
        logging.error("Browser icon not found. Please make sure browser.png exists.")
        return False
    
    time.sleep(3)
    focus_window()
    
    if not focus_search_bar():
        return False
    
    pyautogui.write("gmail.com")
    pyautogui.press("enter")
    logging.info("Navigated to gmail.com")
    
    return True

# ==============================
# Main entry point
# ==============================
if __name__ == "__main__":
    logging.info("Browser Automation Script")
    logging.info("=" * 50)
    logging.info("Please make sure you have the following image files in the same directory:")
    logging.info("browser.png, search_bar.png, compose.png, to.png, subject.png, email.png, send.png")
    
    input("\nPress Enter to start...\n")
    
    if open_browser_and_navigate():
        logging.info("Waiting for Gmail to load...")
        time.sleep(8)  # wait for Gmail UI to load
        if compose_and_send_email():
            logging.info("Automation completed successfully!")
        else:
            logging.error("Failed while composing/sending the email.")
            sys.exit(1)
    else:
        logging.error("Automation encountered issues opening browser.")
        sys.exit(1)
