#!/usr/bin/env python3

# timer.py

import time
import os
import logging
from datetime import datetime, timedelta
from utils import send_notification
from db import log_task
from config import (
    UPDATE_INTERVAL,
    CLEAR_SCREEN,
)
import threading
from terminal_numbers import LARGE_DIGITS  # Importing LARGE_DIGITS
import sys
import select

class Timer:
    def __init__(self, task_name, total_seconds):
        self.task_name = task_name
        self.total_seconds = total_seconds
        self.start_time = datetime.now()
        self.initial_duration_seconds = total_seconds
        self.actual_seconds = 0
        self.user_decision = None
        self.decision_lock = threading.Lock()
        self.prompt_timeout = 30  # Seconds to wait for user input

    def render_large_time(self, time_str, negative=False):
        lines = [""] * 5  # Each digit representation has 5 lines
        for char in time_str:
            digit_lines = LARGE_DIGITS.get(char, ["     "] * 5)
            for i in range(5):
                lines[i] += digit_lines[i] + "  "  # Add space between digits
        # Apply bold styling
        if negative:
            # Apply red color for negative time
            lines = [f"\033[1m\033[31m{line}\033[0m" for line in lines]
        else:
            lines = [f"\033[1m{line}\033[0m" for line in lines]
        return lines

    def prompt_user(self):
        # Function to prompt the user when time is up
        print(f"\nTime is up for '{self.task_name}'.")
        print("Did you finish the task? (y/n): ", end='', flush=True)
        start_time = time.time()
        while time.time() - start_time < self.prompt_timeout:
            if os.name == 'nt':
                # For Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch().lower()
                    if key in ['y', 'n']:
                        with self.decision_lock:
                            self.user_decision = (key == 'y')
                        break
            else:
                # For Unix/Linux
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    response = sys.stdin.readline().strip().lower()
                    if response in ['y', 'n']:
                        with self.decision_lock:
                            self.user_decision = (response == 'y')
                        break
            time.sleep(0.1)
        else:
            print("\nNo response received. Continuing the timer.")

    def listen_for_input(self):
        # Function to listen for 'y' or 'n' input during the timer
        while True:
            if os.name == 'nt':
                # For Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch().lower()
                    if key in ['y', 'n']:
                        with self.decision_lock:
                            self.user_decision = (key == 'y')
            else:
                # For Unix/Linux
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    response = sys.stdin.readline().strip().lower()
                    if response in ['y', 'n']:
                        with self.decision_lock:
                            self.user_decision = (response == 'y')
            time.sleep(0.1)

    def start(self):
        # Start the input listener thread
        input_thread = threading.Thread(target=self.listen_for_input)
        input_thread.daemon = True
        input_thread.start()

        time_up = False
        try:
            while True:
                remaining_seconds = int(self.total_seconds)
                if remaining_seconds >= 0:
                    remaining_time = str(timedelta(seconds=remaining_seconds))
                    negative = False
                else:
                    remaining_time = str(timedelta(seconds=-remaining_seconds))
                    negative = True
                # Ensure format is HH:MM:SS
                if len(remaining_time) < 8:
                    remaining_time = "0" + remaining_time
                if negative:
                    remaining_time = "-" + remaining_time
                large_time_lines = self.render_large_time(remaining_time, negative)
                if CLEAR_SCREEN:
                    os.system('clear' if os.name == 'posix' else 'cls')
                columns, lines_terminal = os.get_terminal_size()
                # Calculate padding to center the large time
                content_height = len(large_time_lines) + 1  # Timer lines + 1 for task name
                space_below_timer = lines_terminal - content_height
                padding_top = (lines_terminal - content_height) // 2 - len(large_time_lines)
                padding_top = max(0, padding_top)
                print('\n' * padding_top)
                for line in large_time_lines:
                    print(line.center(columns))
                padding_between = (space_below_timer - padding_top) // 2
                print('\n' * padding_between)
                task_text = f"TASK: {self.task_name.upper()}"
                task_text = f"\033[1m{task_text}\033[0m"  # Make it bold
                print(task_text.center(columns))

                # Send notification and prompt at time zero
                if not time_up and self.total_seconds <= 0:
                    send_notification(self.task_name)
                    self.prompt_user()
                    time_up = True

                # Continue the timer regardless
                time.sleep(UPDATE_INTERVAL)
                self.total_seconds -= UPDATE_INTERVAL
                self.actual_seconds += UPDATE_INTERVAL
        except KeyboardInterrupt:
            logging.info("Task manually interrupted.")
            print("\nTask ended.")
        finally:
            self.end_time = datetime.now()
            self._finalize()

    def _finalize(self):
        # Use the last decision made by the user
        if self.user_decision is not None:
            completed = self.user_decision
        else:
            # If no decision was made, ask the user now
            print("Did you finish the task? (y/n): ", end='', flush=True)
            response = input().strip().lower()
            completed = (response == 'y')

        total_minutes = self.actual_seconds / 60
        log_task(
            self.task_name,
            self.start_time,
            self.initial_duration_seconds / 60,
            self.end_time,
            total_minutes,
            completed
        )
        send_notification(self.task_name)
        if CLEAR_SCREEN:
            os.system('clear' if os.name == 'posix' else 'cls')
        columns, _ = os.get_terminal_size()
        print(f"{self.task_name} - Timer stopped.".center(columns))