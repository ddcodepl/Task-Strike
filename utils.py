# utils.py

import os
import time
import sys
import logging
from shutil import get_terminal_size
from config import NOTIFICATIONS_ENABLED, SOUND_ENABLED, POPUP_DURATION
import platform

if platform.system() == 'Darwin':
    # We're on macOS
    from pync import Notifier
else:
    from plyer import notification

def center_text(text):
    columns, lines = get_terminal_size()
    padding_top = (lines - 1) // 2
    padding_left = (columns - len(text)) // 2
    return f"{' ' * padding_left}{text}", padding_top

def send_notification(task_name):
    if NOTIFICATIONS_ENABLED:
        try:
            if platform.system() == 'Darwin':
                # Use pync for macOS
                Notifier.notify(
                    message=f"{task_name} - Time's up!",
                    title="TaskStrike Timer",
                    sound='default' if SOUND_ENABLED else None,
                    activate='com.apple.Terminal'  # Replace with your app's bundle ID if needed
                )
            else:
                # Use plyer for other platforms
                notification.notify(
                    title="TaskStrike Timer",
                    message=f"{task_name} - Time's up!",
                    timeout=POPUP_DURATION
                )
                if SOUND_ENABLED:
                    # Implement sound notification if needed
                    pass
        except Exception as e:
            logging.error(f"Notification failed: {e}")
            print(f"Notification failed: {e}")

def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))