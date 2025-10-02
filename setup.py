import os
import win32com.client
import PyInstaller.__main__
import psutil

PROCNAME = "pyscreenshotutil.exe"

for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()

PyInstaller.__main__.run([
    'main.py',                   # your entry point
    '--onedir',                  # bundle into a folder (not single exe)
    '--noconsole',               # no console window
    '--name=pyscreenshotutil',   # exe name
    '--icon=camera2.ico',        # custom icon
])


def create_shortcut(target_path, shortcut_name, subfolder=None, icon_path=None):
    # Convert all paths to absolute
    target_path = os.path.abspath(target_path)
    if icon_path:
        icon_path = os.path.abspath(icon_path)

    # Base Start Menu Programs folder
    start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
    os.makedirs(start_menu, exist_ok=True)

    # If you want a custom subfolder (e.g. "My Apps"), create it
    if subfolder:
        start_menu = os.path.join(start_menu, subfolder)
        os.makedirs(start_menu, exist_ok=True)

    shortcut_path = os.path.join(start_menu, f"{shortcut_name}.lnk")

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    if icon_path:
        shortcut.IconLocation = icon_path
    shortcut.save()

    print(f"✅ Shortcut created at: {shortcut_path}")

# Example usage
exe_path = r"dist\pyscreenshotutil\pyscreenshotutil.exe"
create_shortcut(exe_path, "PyScreenshotUtil", subfolder="JonasB2510 Apps", icon_path=exe_path)
