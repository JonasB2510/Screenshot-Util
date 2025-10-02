import pyautogui
import keyboard
import time
import win32clipboard
from io import BytesIO
from PIL import Image, ImageGrab
import sys
import os
from datetime import datetime
from screeninfo import get_monitors


SCREENSHOTPATH = "screenshots"

def get_mouse_monitor():
    mouse_x, mouse_y = pyautogui.position()

    for monitor in get_monitors():
        if (monitor.x <= mouse_x < monitor.x + monitor.width and
            monitor.y <= mouse_y < monitor.y + monitor.height):
            return monitor
    return None

def open_folder():
    try:
        os.startfile(SCREENSHOTPATH)
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def take_screenshot():
    try:
        print("Taking screenshot...")
        monitor = get_mouse_monitor()
        
        bbox = (monitor.x, monitor.y, 
                monitor.x + monitor.width, 
                monitor.y + monitor.height)
        
        image = ImageGrab.grab(bbox=bbox, all_screens=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(SCREENSHOTPATH, f"screenshot_{timestamp}.png")
        save_path = os.path.join(os.getcwd(), filename)
        image.save(save_path, "PNG")
        print(f"Screenshot saved as {save_path}")

    except Exception as e:
        print(f"Error taking screenshot: {e}")

def main():
    print("Screenshot tool started. Press F10 to take a screenshot, Ctrl+C to exit.")
    
    try:
        os.makedirs(SCREENSHOTPATH, exist_ok=True)
        keyboard.add_hotkey("f9", open_folder)
        keyboard.add_hotkey("f10", take_screenshot)
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
