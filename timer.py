#!/usr/bin/env python3

# timer.py

import time
import os
import logging
from datetime import datetime, timedelta
from utils import send_notification
from db import log_task
from config import (
    UPDATE_INTERVAL,  # Typically set to 1 for a 1-second update interval
    CLEAR_SCREEN,     # Boolean to determine whether to clear the screen on each update
)
from terminal_numbers import LARGE_DIGITS  # Ensure LARGE_DIGITS is a dict mapping characters to large digit representations
import sys
import select
import threading

class Timer:
    def __init__(self, task_name, total_seconds):
        """
        Initializes the Timer with the task name and total duration in seconds.
        """
        self.task_name = task_name
        self.total_seconds = total_seconds
        self.initial_duration_seconds = total_seconds
        self.actual_seconds = 0
        self.user_decision = None
        self.decision_lock = threading.Lock()
        self.prompt_timeout = 30  # Seconds to wait for user input during prompts
        self.end_time = None
        self.continue_task = False  # Flag to indicate if user chose to continue
        self.final_prompt = False  # Flag for the final prompt after negative time

    def render_large_time(self, time_str, negative=False):
        """
        Renders the remaining time in a large, stylized format.
        """
        lines = [""] * 5  # Each digit representation has 5 lines
        for char in time_str:
            digit_lines = LARGE_DIGITS.get(char, ["     "] * 5)
            for i in range(5):
                lines[i] += digit_lines[i] + "  "  # Add space between digits
        # Apply bold styling and color if negative
        if negative:
            # Apply red color for negative time
            lines = [f"\033[1m\033[31m{line}\033[0m" for line in lines]
        else:
            lines = [f"\033[1m{line}\033[0m" for line in lines]
        return lines

    def prompt_user_initial(self):
        """
        Prompts the user to confirm if the task was completed.
        Provides options: 'y' (Yes), 'n' (No), 'c' (Continue).
        """
        print(f"\nTime is up for '{self.task_name}'.")
        print("Did you finish the task? (y/n/c): ", end='', flush=True)
        start_time = time.time()
        response = ''
        while time.time() - start_time < self.prompt_timeout:
            if os.name == 'nt':
                # For Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch().lower()
                    if key in ['y', 'n', 'c']:
                        response = key
                        break
            else:
                # For Unix/Linux
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    response = sys.stdin.readline().strip().lower()
                    if response in ['y', 'n', 'c']:
                        break
            time.sleep(0.1)
        else:
            # Timeout reached
            print("\nNo response received. Defaulting to 'n'.")
            response = 'n'

        if response == '':
            response = 'n'
        if response not in ['y', 'n', 'c']:
            print("Invalid input. Defaulting to 'n'.")
            response = 'n'

        with self.decision_lock:
            if response == 'y':
                self.user_decision = True
            elif response == 'n':
                self.user_decision = False
            elif response == 'c':
                self.continue_task = True
                print("Continuing the task. Press Ctrl+C to stop the timer when done.")
                logging.info(f"User chose to continue the task '{self.task_name}'.")

    def prompt_user_final(self):
        """
        Prompts the user again to confirm if the task was completed.
        Only options: 'y' (Yes), 'n' (No).
        This is used when the timer is in negative time after choosing to continue.
        """
        print(f"\nAdditional time has passed for '{self.task_name}'.")
        print("Did you finish the task? (y/n): ", end='', flush=True)
        start_time = time.time()
        response = ''
        while time.time() - start_time < self.prompt_timeout:
            if os.name == 'nt':
                # For Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch().lower()
                    if key in ['y', 'n']:
                        response = key
                        break
            else:
                # For Unix/Linux
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    response = sys.stdin.readline().strip().lower()
                    if response in ['y', 'n']:
                        break
            time.sleep(0.1)
        else:
            # Timeout reached
            print("\nNo response received. Defaulting to 'n'.")
            response = 'n'

        if response == '':
            response = 'n'
        if response not in ['y', 'n']:
            print("Invalid input. Defaulting to 'n'.")
            response = 'n'

        with self.decision_lock:
            self.user_decision = (response == 'y')

    def listen_for_input(self):
        """
        Function to listen for 'y', 'n', or 'c' input during the timer.
        Sets the user_decision or continue_task accordingly.
        """
        while True:
            if os.name == 'nt':
                # For Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch().lower()
                    if key in ['y', 'n', 'c']:
                        with self.decision_lock:
                            if key == 'y':
                                self.user_decision = True
                                break
                            elif key == 'n':
                                self.user_decision = False
                                break
                            elif key == 'c':
                                self.continue_task = True
                                print("\nContinuing the task. Press Ctrl+C to stop the timer when done.")
                                logging.info(f"User chose to continue the task '{self.task_name}'.")
                                break
            else:
                # For Unix/Linux
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    response = sys.stdin.readline().strip().lower()
                    if response in ['y', 'n', 'c']:
                        with self.decision_lock:
                            if response == 'y':
                                self.user_decision = True
                                break
                            elif response == 'n':
                                self.user_decision = False
                                break
                            elif response == 'c':
                                self.continue_task = True
                                print("\nContinuing the task. Press Ctrl+C to stop the timer when done.")
                                logging.info(f"User chose to continue the task '{self.task_name}'.")
                                break
            time.sleep(0.1)

    def start(self):
        """
        Starts the timer countdown and handles user interactions upon completion or interruption.
        """
        self.start_time = datetime.now()
        logging.info(f"Task '{self.task_name}' started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        # Start the input listener thread
        input_thread = threading.Thread(target=self.listen_for_input)
        input_thread.daemon = True
        input_thread.start()

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
                try:
                    columns, lines_terminal = os.get_terminal_size()
                except OSError:
                    # Default terminal size if unable to get
                    columns, lines_terminal = 80, 24
                # Calculate padding to center the large time
                content_height = len(large_time_lines) + 1  # Timer lines + 1 for task name
                space_below_timer = lines_terminal - content_height
                padding_top = max((lines_terminal - content_height) // 2, 0)
                print('\n' * padding_top)
                for line in large_time_lines:
                    print(line.center(columns))
                padding_between = max((space_below_timer - padding_top) // 2, 0)
                print('\n' * padding_between)
                task_text = f"TASK: {self.task_name.upper()}"
                task_text = f"\033[1m{task_text}\033[0m"  # Make it bold
                print(task_text.center(columns))

                # Check if time is up and prompt hasn't been initiated yet
                if self.total_seconds <= 0 and not self.final_prompt and not self.continue_task:
                    # Time is up, initiate prompt
                    self.prompt_user_initial()

                # Continue the timer
                time.sleep(UPDATE_INTERVAL)
                self.total_seconds -= UPDATE_INTERVAL
                self.actual_seconds += UPDATE_INTERVAL

                # If the user chose to continue, keep the timer running without prompting
                if self.continue_task:
                    continue

        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\nTimer interrupted by user.")
            logging.info(f"Task '{self.task_name}' interrupted by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.end_time = datetime.now()
            if not self.continue_task:
                # If not continuing, prompt for task completion
                self.prompt_user_final()
                self._finalize()
            else:
                # If continuing, prompt final confirmation if time is negative
                if self.total_seconds < 0 and not self.final_prompt:
                    self.final_prompt = True
                    self.prompt_user_final()
                    self._finalize()
                else:
                    # Finalize if time is not negative
                    self._finalize()
        finally:
            if not self.continue_task:
                self.end_time = datetime.now()
                try:
                    self._finalize()
                except Exception as e:
                    logging.error(f"Error during finalization: {e}")
                    print(f"An error occurred during finalization: {e}")

    def _finalize(self):
        """
        Finalizes the task by logging it to the database and sending a notification based on user input.
        """
        # Safely retrieve the user's decision
        with self.decision_lock:
            completed = self.user_decision if self.user_decision is not None else False

        status = "Finished" if completed else "Not Finished"

        total_minutes = self.actual_seconds / 60
        log_task(
            self.task_name,
            self.start_time,
            self.initial_duration_seconds / 60,
            self.end_time,
            total_minutes,
            completed
        )
        send_notification(self.task_name, status=status)
        if CLEAR_SCREEN:
            os.system('clear' if os.name == 'posix' else 'cls')
        try:
            columns, _ = os.get_terminal_size()
        except OSError:
            columns = 80
        print(f"{self.task_name} - Timer {'finished' if completed else 'stopped without completion'}.")
        logging.info(f"Task '{self.task_name}' {'finished' if completed else 'stopped without completion'}.")