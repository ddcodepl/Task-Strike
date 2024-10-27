# timer.py

import time
import os
import logging
from datetime import datetime, timedelta
from utils import center_text, send_notification
from db import log_task
from config import UPDATE_INTERVAL, CLEAR_SCREEN

class Timer:
    def __init__(self, task_name, duration_minutes):
        self.task_name = task_name
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.total_seconds = duration_minutes * 60
        self.actual_seconds = 0

    def start(self):
        try:
            while self.total_seconds > 0:
                remaining_time = timedelta(seconds=self.total_seconds)
                countdown_text = f"{self.task_name} - Time Remaining: {remaining_time}"
                if CLEAR_SCREEN:
                    os.system('clear' if os.name == 'posix' else 'cls')
                centered_text, padding_top = center_text(countdown_text)
                print("\n" * padding_top + centered_text)
                time.sleep(UPDATE_INTERVAL)
                self.total_seconds -= UPDATE_INTERVAL
                self.actual_seconds += UPDATE_INTERVAL
        except KeyboardInterrupt:
            logging.info("Task manually interrupted.")
            print("\nTask manually interrupted.")
        finally:
            self.end_time = datetime.now()
            self._finalize()

    def _finalize(self):
        completed = input("Did you finish the task? (y/n): ").strip().lower() == 'y'
        log_task(
            self.task_name,
            self.start_time,
            self.duration_minutes,
            self.end_time,
            int(self.actual_seconds // 60),
            completed
        )
        send_notification(self.task_name)
        if CLEAR_SCREEN:
            os.system('clear' if os.name == 'posix' else 'cls')
        print(center_text(f"{self.task_name} - Time's up!")[0])
