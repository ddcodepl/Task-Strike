# utils.py

import os
import time
from shutil import get_terminal_size
from plyer import notification
from config import NOTIFICATIONS_ENABLED, SOUND_ENABLED, POPUP_DURATION
import logging

def center_text(text):
    columns, lines = get_terminal_size()
    padding_top = (lines - 1) // 2
    padding_left = (columns - len(text)) // 2
    return f"{' ' * padding_left}{text}", padding_top

def send_notification(task_name):
    if NOTIFICATIONS_ENABLED:
        notification.notify(
            title="TaskStrike Timer",
            message=f"{task_name} - Time's up!",
            timeout=POPUP_DURATION
        )
        if SOUND_ENABLED:
            # Implement sound notification (platform-dependent)
            pass

def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))
