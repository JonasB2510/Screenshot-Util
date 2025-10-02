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

try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    HAS_CUSTOMTKINTER = False
    print("customtkinter not found, using regular tkinter")

EXENAME = "pyscreenshotutil.exe"
SCREENSHOTPATH = "screenshots"
SETTINGS_FILE = "settings.json"

class ScreenshotTool:
    def __init__(self):
        self.settings = self.load_settings()
        self.icon = None
        self.settings_window = None
        self.setup_hotkeys()
        
    def load_settings(self):
        """Lade Einstellungen aus JSON oder verwende Standardwerte"""
        default_settings = {
            "screenshot_key": "f10",
            "open_folder_key": "f9",
            "screenshot_path": SCREENSHOTPATH
        }
        
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    return {**default_settings, **settings}
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Speichere Einstellungen in JSON"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved!")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    
    def setup_hotkeys(self):
        """Registriere die Hotkeys basierend auf den Einstellungen"""
        try:
            # Entferne alle existierenden Hotkeys
            keyboard.unhook_all()
            
            # Registriere neue Hotkeys
            keyboard.add_hotkey(self.settings["screenshot_key"], self.take_screenshot, suppress=False)
            keyboard.add_hotkey(self.settings["open_folder_key"], self.open_folder, suppress=False)
            print(f"Hotkeys: {self.settings['screenshot_key']} (screenshot), {self.settings['open_folder_key']} (folder)")
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
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
            print(f"Error opening folder: {e}")
    
    def take_screenshot(self):
        """Mache einen Screenshot des aktuellen Monitors"""
        try:
            print("Taking screenshot...")
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
            print(f"Screenshot saved: {save_path}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
    
    def open_settings_window(self):
        """Öffne das Einstellungsfenster"""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        
        if HAS_CUSTOMTKINTER:
            self.create_customtkinter_settings()
        else:
            #kp wieso claude
            self.create_tkinter_settings()
    
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
    
    def create_tkinter_settings(self):
        """Erstelle Einstellungsfenster mit regulärem Tkinter"""
        self.settings_window = tk.Tk()
        self.settings_window.title("Screenshot Tool - Settings")
        self.settings_window.geometry("400x200")
        self.settings_window.resizable(False, False)
        self.settings_window.configure(bg='#2b2b2b')
        
        # Header
        header = tk.Label(
            self.settings_window, 
            text="⚙️ Keybindings",
            font=("Arial", 16, "bold"),
            bg='#2b2b2b',
            fg='white'
        )
        header.pack(pady=15)
        
        # Frame
        frame = tk.Frame(self.settings_window, bg='#3b3b3b')
        frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Screenshot Key
        tk.Label(frame, text="Screenshot Key:", bg='#3b3b3b', fg='white').grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.screenshot_key_var = tk.StringVar(value=self.settings["screenshot_key"])
        tk.Entry(frame, textvariable=self.screenshot_key_var, width=15).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(frame, text="Change", command=lambda: self.listen_for_key("screenshot_key")).grid(row=0, column=2, padx=10, pady=10)
        
        # Folder Key
        tk.Label(frame, text="Open Folder Key:", bg='#3b3b3b', fg='white').grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.folder_key_var = tk.StringVar(value=self.settings["open_folder_key"])
        tk.Entry(frame, textvariable=self.folder_key_var, width=15).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(frame, text="Change", command=lambda: self.listen_for_key("open_folder_key")).grid(row=1, column=2, padx=10, pady=10)
        
        # Save Button
        tk.Button(self.settings_window, text="Save Settings", command=self.save_from_window, bg='#0078d7', fg='white', height=2).pack(pady=10)
        
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_window)
        self.settings_window.mainloop()
    
    def listen_for_key(self, action):
        """Warte auf Tastendruck"""
        print(f"Press new key for {action}...")
        
        def on_key(event):
            new_key = event.name
            if action == "screenshot_key":
                self.screenshot_key_var.set(new_key)
            else:
                self.folder_key_var.set(new_key)
            keyboard.unhook(hook)
            print(f"Key set to: {new_key}")
        
        hook = keyboard.on_press(on_key, suppress=False)
    
    def save_from_window(self):
        """Speichere Einstellungen aus dem Fenster"""
        self.settings["screenshot_key"] = self.screenshot_key_var.get()
        self.settings["open_folder_key"] = self.folder_key_var.get()
        self.save_settings()
        self.setup_hotkeys()
        print("Settings saved and hotkeys updated!")
    
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
        print("Exiting...")
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
        
        print("Screenshot Tool started!")
        print(f"Screenshot key: {self.settings['screenshot_key']}")
        print(f"Open folder key: {self.settings['open_folder_key']}")
        print("Check system tray for settings...")
        
        tray_thread = threading.Thread(target=self.run_tray, daemon=False)
        tray_thread.start()
        tray_thread.join()

if __name__ == "__main__":
    try:
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
        if is_running(EXENAME):
            messagebox.showerror("Error while starting program!", f"An instance of {EXENAME} has been detected. Please close out of the old instance to satrt a new one!")
            sys.exit(1)
        else:
            tool = ScreenshotTool()
            tool.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)