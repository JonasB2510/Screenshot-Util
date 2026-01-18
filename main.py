import pystray
from PIL import Image, ImageDraw, ImageGrab
import threading
import pyautogui
import keyboard
import os
import sys
from datetime import datetime
from screeninfo import get_monitors
import json
import psutil
import ctypes
from tkinter import messagebox
import socket
import customtkinter as ctk
import time
import logging

HOTKEY_REFRESH_INTERVAL = 60 * 60  # 60 minutes
CHECK_INTERVAL = 5                 # 5 seconds

EXENAME = "pyscreenshotutil.exe"
SCREENSHOTPATH = "screenshots"
SETTINGS_FILE = "settings.json"

LOG_DIR = "logs"

class HotkeyManager:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True
        )

    def start(self):
        self.register_hotkeys()
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.unregister_hotkeys()

    def register_hotkeys(self):
        #print("Registering hotkeys...")
        logger.info("Registering hotkeys...")
        tool = ScreenshotTool()
        tool.setup_hotkeys()
        # YOUR HOTKEY REGISTRATION CODE HERE
        # Example:
        # keyboard.add_hotkey('ctrl+shift+s', self.take_screenshot)

    def unregister_hotkeys(self):
        #print("Unregistering hotkeys...")
        logger.info("Unregistering hotkeys...")
        # Clean up old hotkeys here
        # Example:
        keyboard.unhook_all_hotkeys()

    def _watchdog_loop(self):
        last_refresh = time.time()

        while not self.stop_event.is_set():
            time.sleep(CHECK_INTERVAL)

            # Refresh hotkeys every 30 minutes
            if time.time() - last_refresh >= HOTKEY_REFRESH_INTERVAL:
                logger.debug("Refreshing hotkeys...")
                #print("Refreshing hotkeys...")
                self.unregister_hotkeys()
                self.register_hotkeys()
                last_refresh = time.time()

        logger.warning("Hotkey watchdog thread stopped.")
        #print("Hotkey watchdog thread stopped.")

class ScreenshotTool:
    def __init__(self):
        self.settings = self.load_settings()
        self.icon = None
        self.settings_window = None
        #self.setup_hotkeys()
        
    def load_settings(self):
        """Lade Einstellungen aus JSON oder verwende Standardwerte"""
        default_settings = {
            "screenshot_key": "f10",
            "open_folder_key": "f9",
            "screenshot_path": SCREENSHOTPATH,
            "logs_path": LOG_DIR
        }
        
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    return {**default_settings, **settings}
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            #print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        global logger
        """Speichere Einstellungen in JSON"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved!")
            #print("Settings saved!")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            #print(f"Error saving settings: {e}")
            
    
    def setup_hotkeys(self):
        """Registriere die Hotkeys basierend auf den Einstellungen"""
        try:
            # Entferne alle existierenden Hotkeys
            keyboard.unhook_all()
            
            # Registriere neue Hotkeys
            keyboard.add_hotkey(self.settings["screenshot_key"], self.take_screenshot, suppress=False)
            keyboard.add_hotkey(self.settings["open_folder_key"], self.open_folder, suppress=False)
            logger.info(f"Hotkeys: {self.settings['screenshot_key']} (screenshot), {self.settings['open_folder_key']} (folder)")
            #print(f"Hotkeys: {self.settings['screenshot_key']} (screenshot), {self.settings['open_folder_key']} (folder)")
        except Exception as e:
            logger.error(f"Error setting up hotkeys: {e}")
            #print(f"Error setting up hotkeys: {e}")
    
    def get_mouse_monitor(self):
        """Finde den Monitor, auf dem sich die Maus befindet"""
        mouse_x, mouse_y = pyautogui.position()
        
        for monitor in get_monitors():
            if (monitor.x <= mouse_x < monitor.x + monitor.width and
                monitor.y <= mouse_y < monitor.y + monitor.height):
                return monitor
        return get_monitors()[0]
    
    def open_folder(self):
        """Öffne den Screenshot-Ordner"""
        try:
            screenshot_path = self.settings["screenshot_path"]
            os.makedirs(screenshot_path, exist_ok=True)
            os.startfile(screenshot_path)
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            #print(f"Error opening folder: {e}")
    
    def take_screenshot(self):
        """Mache einen Screenshot des aktuellen Monitors"""
        try:
            logger.info("Taking screenshot...")
            #print("Taking screenshot...")
            monitor = self.get_mouse_monitor()
            
            bbox = (monitor.x, monitor.y, 
                    monitor.x + monitor.width, 
                    monitor.y + monitor.height)
            
            image = ImageGrab.grab(bbox=bbox, all_screens=True)
            
            screenshot_path = self.settings["screenshot_path"]
            os.makedirs(screenshot_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(screenshot_path, f"screenshot_{timestamp}.png")
            save_path = os.path.join(os.getcwd(), filename)
            image.save(save_path, "PNG")
            logger.info(f"Screenshot saved: {save_path}")
            #print(f"Screenshot saved: {save_path}")
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            #print(f"Error taking screenshot: {e}")
    
    def open_settings_window(self):
        """Öffne das Einstellungsfenster"""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        
        self.create_customtkinter_settings()
    
    def create_customtkinter_settings(self):
        """Erstelle Einstellungsfenster mit CustomTkinter"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.settings_window = ctk.CTk()
        self.settings_window.title("Screenshot Tool - Settings")
        self.settings_window.geometry("500x350")
        self.settings_window.resizable(False, False)
        
        # Header
        header = ctk.CTkLabel(
            self.settings_window, 
            text="Keybindings", #⚙️ 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=20)
        
        # Frame für Keybindings
        frame = ctk.CTkFrame(self.settings_window)
        frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Screenshot Key
        screenshot_label = ctk.CTkLabel(frame, text="Screenshot Key:", font=ctk.CTkFont(size=14))
        screenshot_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.screenshot_key_var = ctk.StringVar(value=self.settings["screenshot_key"])
        screenshot_entry = ctk.CTkEntry(frame, textvariable=self.screenshot_key_var, width=100)
        screenshot_entry.grid(row=0, column=1, padx=20, pady=15)
        
        screenshot_btn = ctk.CTkButton(
            frame, 
            text="Change", 
            command=lambda: self.listen_for_key("screenshot_key"),
            width=80
        )
        screenshot_btn.grid(row=0, column=2, padx=10, pady=15)
        
        # Open Folder Key
        folder_label = ctk.CTkLabel(frame, text="Open Folder Key:", font=ctk.CTkFont(size=14))
        folder_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        
        self.folder_key_var = ctk.StringVar(value=self.settings["open_folder_key"])
        folder_entry = ctk.CTkEntry(frame, textvariable=self.folder_key_var, width=100)
        folder_entry.grid(row=1, column=1, padx=20, pady=15)
        
        folder_btn = ctk.CTkButton(
            frame, 
            text="Change", 
            command=lambda: self.listen_for_key("open_folder_key"),
            width=80
        )
        folder_btn.grid(row=1, column=2, padx=10, pady=15)
        
        # Save Button
        save_btn = ctk.CTkButton(
            self.settings_window, 
            text="Save Settings",
            command=self.save_from_window,
            height=35
        )
        save_btn.pack(pady=15)
        
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_window)
        self.settings_window.mainloop()
    
    def listen_for_key(self, action):
        """Warte auf Tastendruck"""
        #print(f"Press new key for {action}...")
        
        def on_key(event):
            new_key = event.name
            if action == "screenshot_key":
                self.screenshot_key_var.set(new_key)
            else:
                self.folder_key_var.set(new_key)
            keyboard.unhook(hook)
            logger.info(f"Key set to: {new_key} for {action}")
            #print(f"Key set to: {new_key} for {action}")
        
        hook = keyboard.on_press(on_key, suppress=False)
    
    def save_from_window(self):
        """Speichere Einstellungen aus dem Fenster"""
        self.settings["screenshot_key"] = self.screenshot_key_var.get()
        self.settings["open_folder_key"] = self.folder_key_var.get()
        self.save_settings()
        self.setup_hotkeys()
        logger.info("Settings saved and hotkeys updated!")
        #print("Settings saved and hotkeys updated!")
    
    def close_settings_window(self):
        """Schließe das Einstellungsfenster"""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
    
    def create_icon_image(self):
        """Erstelle ein Icon für die System Tray"""
        image = Image.new('RGB', (64, 64), (30, 30, 30))
        d = ImageDraw.Draw(image)
        
        # Kamera zeichnen
        d.rectangle((10, 20, 54, 50), fill=(200, 200, 200), outline=(255, 255, 255))
        d.ellipse((22, 28, 42, 48), fill=(100, 100, 100))
        d.rectangle((44, 24, 52, 30), fill=(150, 150, 150))
        
        return image
    
    def on_quit(self, icon, item):
        """Beende das Programm"""
        #print("Exiting...")
        logger.warning("Exiting...")
        icon.stop()
        os._exit(0)
    
    def create_menu(self):
        """Erstelle das Tray-Menü"""
        return pystray.Menu(
            pystray.MenuItem("Take Screenshot", lambda: self.take_screenshot()),
            pystray.MenuItem("Open Folder", lambda: self.open_folder()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", lambda: threading.Thread(target=self.open_settings_window, daemon=True).start()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_quit)
        )
    
    def run_tray(self):
        """Starte das System Tray Icon"""
        self.icon = pystray.Icon(
            "screenshot_tool",
            self.create_icon_image(),
            "Screenshot Tool",
            menu=self.create_menu()
        )
        self.icon.run()
    
    def run(self):
        """Starte das gesamte Programm"""
        os.makedirs(self.settings["screenshot_path"], exist_ok=True)
        
        logger.info("Screenshot Tool started!")
        logger.info(f"Screenshot key: {self.settings['screenshot_key']}")
        logger.info(f"Open folder key: {self.settings['open_folder_key']}")
        logger.info("Check system tray for settings...")
        #print("Screenshot Tool started!")
        #print(f"Screenshot key: {self.settings['screenshot_key']}")
        #print(f"Open folder key: {self.settings['open_folder_key']}")
        #print("Check system tray for settings...")
        
        tray_thread = threading.Thread(target=self.run_tray, daemon=False)
        tray_thread.start()
        tray_thread.join()

def ipc_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 50555))
    s.listen(1)

    while True:
        conn, _ = conn_info = s.accept()
        msg = conn.recv(1024).decode()
        if msg == "opened_app":
            screenshot_tool = ScreenshotTool()
            screenshot_tool.open_settings_window()
            logger.warning("Opening settings because of external request!")
            #pass
        conn.close()


def notify_existing_instance():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 50555))
        s.send(b"opened_app")
        s.close()
        return True
    except ConnectionRefusedError:
        return False

def define_logger(title=None):
    global logger

    tool = ScreenshotTool()
    data = tool.load_settings()
    if title == None:
        LATEST_LOG = os.path.join(data["logs_path"], "latest.log")
    else:
        LATEST_LOG = os.path.join(data["logs_path"], f"{title}.log")
    os.makedirs(data["logs_path"], exist_ok=True)

    # If latest.log exists, rename it with last modified time
    if title == None:
        if os.path.exists(LATEST_LOG):
            mtime = os.path.getmtime(LATEST_LOG)
            timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d_%H-%M-%S")
            archived_log = os.path.join(data["logs_path"], f"{timestamp}.log")
            os.rename(LATEST_LOG, archived_log)

    # Configure logging
    logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LATEST_LOG),
        logging.StreamHandler()  # still prints to console
    ]
    )

    logger = logging.getLogger("PySSUtil")
    logger.debug("Logger started!")

if __name__ == "__main__":
    try:
        logger_messages = []
        print(os.getenv("pyscreenshotutil_config"))
        if os.getenv("pyscreenshotutil_config"):
            SETTINGS_FILE = os.getenv("pyscreenshotutil_config")
        logger_messages.append((f"Settingsfile configured: {SETTINGS_FILE}", logging.DEBUG))
        def is_running(exe_name):
            exe_name = exe_name.lower()
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.pid == current_pid:
                        continue  # skip this process itself
                    if proc.info['name'] and proc.info['name'].lower() == exe_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        check_quit = False
        if is_running(EXENAME):
            logger_messages.append((F"Error while starting program: An instance of {EXENAME} has been detected. This instance is closing now!", logging.ERROR))
            #messagebox.showerror("Error while starting program!", f"An instance of {EXENAME} has been detected. Please close out of the old instance to satrt a new one!")
            if notify_existing_instance():
                pass
            else:
                logger_messages.append(("Error while trying to contact the already running program", logging.ERROR))
                messagebox.showerror("Error", "Error while trying to contact the already running program")
            check_quit = True

        if check_quit == True:
            define_logger(title=f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_error")
        else:
            define_logger()
        for msg in logger_messages:
            logger.log(msg[1], msg[0])
        if check_quit == True:
            logger.warning("Exiting...")
            sys.exit(1)
        threading.Thread(target=ipc_server, daemon=True).start()
        hotkeys = HotkeyManager()
        hotkeys.start()
        tool = ScreenshotTool()
        tool.run()
    except KeyboardInterrupt:
        #logger.warning("Exiting...")
        #print("\nExiting...")
        tool.on_quit()
        sys.exit(0)
    except Exception as e:
        define_logger()
        logger.error(f"Error: {e}")
        #print(f"Error: {e}")
        sys.exit(1)