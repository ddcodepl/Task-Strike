# utils.py

import os
import time
import sys
import logging
from shutil import get_terminal_size
from config import NOTIFICATIONS_ENABLED, SOUND_ENABLED, POPUP_DURATION
import platform
import subprocess

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


def send_notification(task_name, status=None):
    """
    Sends a desktop notification about the task status.

    Args:
        task_name (str): The name of the task.
        status (str, optional): The status of the task ('Finished' or 'Not Finished').
    """
    if status:
        message = f"Task '{task_name}' {status}."
    else:
        message = f"Task '{task_name}' completed."

    system = platform.system()

    if system == "Darwin":  # macOS
        subprocess.run(["osascript", "-e",
                        f'display notification "{message}" with title "TaskStrike"'])
    elif system == "Linux":
        subprocess.run(["notify-send", "TaskStrike", message])
    elif system == "Windows":
        # For Windows, you might need to install `win10toast` or use a similar library
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast("TaskStrike", message, duration=5, threaded=True)
        except ImportError:
            print("Notification not supported on Windows without 'win10toast' library.")
    else:
        print(message)  # Fallback to console output if OS is not supported

def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))