# main.py

import argparse
import logging
from tabulate import tabulate
from db import (
    initialize_db,
    add_task_to_todo,
    fetch_todo_list,
    fetch_task_history,
)
from timer import Timer
from config import (
    DEFAULT_DURATION,
    LOG_LEVEL,
    LOG_FILE,
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

def add_task(task_name, duration_minutes):
    if task_name and duration_minutes:
        add_task_to_todo(task_name, duration_minutes)
        print(f"Task '{task_name}' added to the to-do list.")
    else:
        print("Please provide both a task name and duration to add a task.")

def show_history():
    tasks = fetch_task_history()
    task_data = [
        [
            task.task_name,
            task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            task.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            task.initial_duration,
            task.actual_duration,
            task.status,
        ]
        for task in tasks
    ]
    print("\nTask History:\n")
    print(
        tabulate(
            task_data,
            headers=[
                "Task Name",
                "Start Time",
                "End Time",
                "Initial Duration",
                "Actual Duration",
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
            todo.duration,
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

if __name__ == "__main__":
    initialize_db()
    logging.info("Application started.")

    parser = argparse.ArgumentParser(
        description="TaskStrike - Pomodoro-style timer with task logging."
    )
    parser.add_argument("task_name", nargs="?", type=str, help="Name of the task.")
    parser.add_argument(
        "duration_minutes", nargs="?", type=int, help="Duration of the task in minutes."
    )
    parser.add_argument(
        "--add-task", "-a", action="store_true", help="Add a task to the to-do list."
    )
    parser.add_argument(
        "--show-history", "-s", action="store_true", help="Display the task history."
    )
    parser.add_argument(
        "--show-todo", "-t", action="store_true", help="Display the to-do list."
    )

    args = parser.parse_args()

    if args.show_history:
        show_history()
    elif args.show_todo:
        show_todo_list()
    elif args.add_task:
        add_task(args.task_name, args.duration_minutes)
    else:
        task_name = args.task_name or "Unnamed Task"
        duration_minutes = args.duration_minutes or DEFAULT_DURATION
        timer = Timer(task_name, duration_minutes)
        timer.start()
