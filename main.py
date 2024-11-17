#!/usr/bin/env python3

# main.py

import argparse
import logging
import os
import sys
from tabulate import tabulate
from db import (
    initialize_db,
    add_task_to_todo,
    fetch_todo_list,
    fetch_task_history,
    delete_task_by_id,
)
from timer import Timer
from config import (
    DEFAULT_DURATION,
    LOG_LEVEL,
    LOG_FILE,
    DB_PATH,  # Import DB_PATH to handle pruning
)
from models import Task, Todo

# Configure logging
numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {LOG_LEVEL}')
logging.basicConfig(
    level=numeric_level,
    filename=LOG_FILE if LOG_FILE else None,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def parse_duration(duration_str):
    try:
        if ':' in duration_str:
            # Split the input into minutes and seconds
            minutes_str, seconds_str = duration_str.split(':')
            minutes = int(minutes_str)
            seconds = int(seconds_str)
        else:
            # Assume the input is an integer representing minutes
            minutes = int(duration_str)
            seconds = 0
        # Normalize seconds if >= 60
        extra_minutes, seconds = divmod(seconds, 60)
        minutes += extra_minutes
        total_seconds = minutes * 60 + seconds
        return total_seconds
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid duration format: '{duration_str}'. Use MM or MM:SS.")


def add_task(task_name, duration_input):
    if task_name and duration_input:
        try:
            total_seconds = parse_duration(duration_input)
            duration_minutes = total_seconds / 60
            add_task_to_todo(task_name, duration_minutes)
            print(f"Task '{task_name}' added to the to-do list.")
            logging.info(f"Added task '{task_name}' with duration {duration_minutes} minutes.")
        except argparse.ArgumentTypeError as e:
            print(e)
    else:
        print("Please provide both a task name and duration to add a task.")


def show_history():
    tasks = fetch_task_history()
    task_data = [
        [
            task.id,
            task.task_name,
            task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            task.end_time.strftime("%Y-%m-%d %H:%M:%S") if task.end_time else "N/A",
            f"{task.initial_duration:.2f}",
            f"{task.actual_duration:.2f}" if task.actual_duration else "N/A",
            task.status,
        ]
        for task in tasks
    ]
    print("\nTask History:\n")
    print(
        tabulate(
            task_data,
            headers=[
                "ID",
                "Task Name",
                "Start Time",
                "End Time",
                "Initial Duration (min)",
                "Actual Duration (min)",
                "Status",
            ],
            tablefmt="fancy_grid",
        )
    )


def show_todo_list():
    todo_list = fetch_todo_list()
    todo_data = [
        [
            todo.task_name,
            f"{todo.duration:.2f}",
            todo.added_date.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        for todo in todo_list
    ]
    print("\nTo-Do List:\n")
    print(
        tabulate(
            todo_data,
            headers=["Task Name", "Duration (minutes)", "Added Date"],
            tablefmt="fancy_grid",
        )
    )


def delete_task(task_id):
    confirm = input(f"Are you sure you want to delete task ID {task_id}? (y/n): ").strip().lower()
    if confirm == 'y':
        delete_task_by_id(task_id)
        print(f"Task ID {task_id} has been deleted.")
        logging.info(f"Deleted task with ID {task_id}.")
    else:
        print("Deletion cancelled.")
        logging.info(f"Deletion cancelled for task ID {task_id}.")


def prune_db():
    """
    Deletes the existing database file and initializes a new one.
    """
    confirm = input(f"Are you sure you want to completely erase the database and start fresh? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Prune database operation cancelled.")
        logging.info("Prune database operation cancelled by user.")
        return

    # Attempt to delete the database file
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"Database '{DB_PATH}' has been deleted.")
            logging.info(f"Deleted database file at '{DB_PATH}'.")
        else:
            print(f"No database file found at '{DB_PATH}'.")
            logging.warning(f"Attempted to delete non-existent database file at '{DB_PATH}'.")

        # Re-initialize the database
        initialize_db()
        print("A new database has been created.")
        logging.info("Initialized a new database.")
    except Exception as e:
        print(f"An error occurred while pruning the database: {e}")
        logging.error(f"Error pruning database: {e}")


def main():
    initialize_db()
    logging.info("Application started.")

    parser = argparse.ArgumentParser(
        description="TaskStrike - Pomodoro-style timer with task logging."
    )

    # Define mutually exclusive group to prevent conflicting arguments
    group = parser.add_mutually_exclusive_group()

    # Task management arguments
    group.add_argument("--add-task", "-a", action="store_true", help="Add a task to the to-do list.")
    group.add_argument("--show-history", "-s", action="store_true", help="Display the task history.")
    group.add_argument("--show-todo", "-t", action="store_true", help="Display the to-do list.")
    group.add_argument("--delete-task", "-d", type=int, help="Delete a task from the history by ID.")
    group.add_argument("--prune-db", "-p", action="store_true",
                       help="Completely remove the database and create a new one.")

    # Positional arguments for starting the timer
    parser.add_argument("task_name", nargs="?", type=str, help="Name of the task.")
    parser.add_argument(
        "duration", nargs="?", type=str, help="Duration of the task in minutes or MM:SS format."
    )

    args = parser.parse_args()

    if args.prune_db:
        prune_db()
    elif args.show_history:
        show_history()
    elif args.show_todo:
        show_todo_list()
    elif args.delete_task is not None:
        delete_task(args.delete_task)
    elif args.add_task:
        add_task(args.task_name, args.duration)
    else:
        # Starting the timer
        task_name = args.task_name or "Unnamed Task"
        duration_input = args.duration or str(DEFAULT_DURATION)
        try:
            total_seconds = parse_duration(duration_input)
            timer = Timer(task_name, total_seconds)
            timer.start()
        except argparse.ArgumentTypeError as e:
            print(e)
            logging.error(f"Failed to start timer: {e}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        logging.info("Application interrupted by user.")
        sys.exit(0)