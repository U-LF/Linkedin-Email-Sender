import pyautogui
import pytesseract
from PIL import Image, ImageChops
import time
import logging
import re
import sys

# ==============================
# Configurable constants
# ==============================
DEFAULT_CONFIDENCE = 0.8
DEFAULT_TIMEOUT = 10
BROWSER_ICON = "browser.png"
SEARCH_BAR_ICON = "search_bar.png"

# Hardcoded single region (x, y, width, height) for responses
TEXT_REGION = (415, 174, 1295, 768)   # Example coordinates for LLM response area

# Scroll behavior
SCROLL_AMOUNT = -400

# ==============================
# Logging setup
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# Helpers
# ==============================
def capture_region(region):
    """Take a screenshot of the given region."""
    x, y, w, h = region
    return pyautogui.screenshot(region=(x, y, w, h))

def has_changed(img1, img2):
    """Check if two images differ."""
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None

def ocr_image(img: Image.Image):
    """Extract and clean text from image using OCR."""
    raw_text = pytesseract.image_to_string(img)
    return clean_text(raw_text)

def clean_text(text):
    """Clean OCR text output by removing junk lines."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        if re.match(r'^[\|\-\+\=\(\)@#]+$', line):
            continue
        if "ChatGPT can make mistakes" in line:
            continue
        cleaned.append(line)
    return " ".join(cleaned)

def click_icon(icon_path, confidence=DEFAULT_CONFIDENCE, timeout=DEFAULT_TIMEOUT):
    """Click an icon on screen by image matching."""
    logging.info(f"Looking for {icon_path}...")
    start_time = time.time()
    wait_time = 0.5

    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateCenterOnScreen(icon_path, confidence=confidence)
        except Exception as e:
            logging.error(f"Error finding {icon_path}: {e}")
            return False

        if location:
            pyautogui.click(location)
            logging.info(f"Clicked {icon_path} at {location}")
            return True
        time.sleep(wait_time)
        wait_time = min(wait_time * 1.5, 5)
    
    logging.error(f"Timeout: Could not find {icon_path}")
    return False

def focus_search_bar():
    """Focus the browser search bar."""
    if click_icon(SEARCH_BAR_ICON, timeout=5):
        return True
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1)
    return click_icon(SEARCH_BAR_ICON, timeout=2)

def open_browser_and_navigate():
    """Open the browser and navigate to ChatGPT page."""
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

def send_query(query):
    """Send a query to the LLM (active input box assumed)."""
    pyautogui.write(query)
    pyautogui.press("enter")
    logging.info(f"Query sent: {query}")
    return True

def collect_text(region):
    """Scroll through the region and collect OCR text."""
    collected_text = []
    seen_chunks = set()

    logging.info("🔼 Scrolling up first...")
    for _ in range(5):
        pyautogui.scroll(800)
        time.sleep(0.5)

    logging.info("⏳ Collecting text by scanning downward...")
    last_img = None
    scroll_attempts = 0

    while True:
        img = capture_region(region)

        if last_img is None or has_changed(last_img, img):
            text_chunk = ocr_image(img)
            if text_chunk and text_chunk not in seen_chunks:
                collected_text.append(text_chunk)
                seen_chunks.add(text_chunk)
                logging.info("📖 Captured new text chunk.")

            last_img = img
            scroll_attempts = 0
        else:
            scroll_attempts += 1
            if scroll_attempts > 3:
                logging.info("✅ Finished scanning full region.")
                break

        pyautogui.scroll(SCROLL_AMOUNT)
        time.sleep(1)

    full_text = "\n".join(collected_text)

    print("\n================= FINAL EXTRACTED TEXT =================")
    print(full_text)
    print("========================================================\n")

    return full_text

# ==============================
# Main entry point
# ==============================
if __name__ == "__main__":
    logging.info("ChatGPT Automation Script")
    input("\nPress Enter to start...\n")

    if open_browser_and_navigate():
        logging.info("Waiting for ChatGPT to load...")
        time.sleep(10)

        # First query
        if send_query("Hello ChatGPT, can you introduce yourself?"):
            time.sleep(5)
            response1 = collect_text(TEXT_REGION)
            logging.info(f"First response captured:\n{response1}")

        # Second query
        time.sleep(5)
        if send_query("Can you explain AI in 500 words?"):
            time.sleep(5)
            response2 = collect_text(TEXT_REGION)
            logging.info(f"Second response captured:\n{response2}")
    else:
        sys.exit(1)
