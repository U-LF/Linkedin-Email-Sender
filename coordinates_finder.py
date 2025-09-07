import mouse
import pyautogui
import time

def on_left_click():
    x, y = pyautogui.position()
    print(f"X: {x}, Y: {y}")

def on_right_click():
    print("Exiting...")
    mouse.unhook_all()
    global running
    running = False

print("Left click = show coordinates, Right click = exit.")

mouse.on_click(lambda: on_left_click())
mouse.on_right_click(lambda: on_right_click())

# Keep program alive until right click exits
running = True
while running:
    time.sleep(0.1)
