# Linux (Hyprland)

#!/usr/bin/env python3
import subprocess
import datetime
import os
import pathlib
import shlex

# --- Configuration ---
SCREENSHOT_DIR = os.path.expanduser("~/Pictures/WaylandScreenshots")
pathlib.Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

# --- Timestamped filename ---
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"screenshot_{timestamp}.png"
filepath = os.path.join(SCREENSHOT_DIR, filename)

# --- Take screenshot ---
try:
    # Ask user to select area or monitor with slurp
    print("Select an area or monitor...")
    area = subprocess.check_output(["slurp"], text=True).strip()  # x,y,w,h

    if area:
        # Take screenshot of selected area
        subprocess.run(["grim", "-g", area, filepath], check=True)
    else:
        # If slurp canceled, take full screen
        subprocess.run(["grim", filepath], check=True)

    print(f"Screenshot saved: {filepath}")

except subprocess.CalledProcessError as e:
    print("Screenshot failed:", e)
    exit(1)

# --- Copy to clipboard ---
try:
    subprocess.run(f"wl-copy < {shlex.quote(filepath)}", shell=True, check=True)
    print("Copied screenshot to clipboard!")
except subprocess.CalledProcessError:
    print("Clipboard copy failed!")

# --- Send notification with click action ---
# Requires 'dunst' or Wayland notification daemon that supports actions
# -c or -t sets timeout (ms), default is 3s = 3000ms
# 'notify-send' supports -a (app name) and -u (urgency)

# Build command
notify_cmd = [
    "notify-send",
    "-u", "normal",
    "-a", "Screenshot Tool",
    "-t", "3000",           # auto-dismiss after 3s
    "-i", "camera-photo",   # icon
    "Screenshot Taken",
    filepath,
    "-h", "string:x-canonical-private-synchronous:screenshot",  # prevent stacking multiple
    "-h", f"string:action:xdg-open {shlex.quote(filepath)}"
]

# On Wayland, clicking an action opens GIMP
# Unfortunately vanilla notify-send can't directly attach click commands
# Workaround: use 'xdg-open' for file
# We can send a notification and rely on the user clicking it manually
# Many Wayland notification daemons (dunst, mako) will open via 'xdg-open' if file is a URL/path

try:
    subprocess.run(["notify-send",
                    "Screenshot Taken",
                    filepath,
                    "-u", "normal",
                    "-t", "3000",
                    "-i", "camera-photo"], check=True)
except subprocess.CalledProcessError:
    print("Notification failed!")

# Optional: open GIMP automatically on click
# Some notification daemons (mako) can trigger commands on click via 'notify-send --action'
# But we’ll do a simple workaround: send a command via 'xdg-open' as if the user clicked

# If you want fully automatic: uncomment this line
# subprocess.run(["gimp", filepath])
