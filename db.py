# db.py

import sqlite3
import sys
import logging
from datetime import datetime
from models import Task, Todo
from queries import (
    CREATE_TASKS_TABLE,
    INSERT_TASK,
    SELECT_TASK_HISTORY,
    CREATE_TODO_TABLE,
    INSERT_TODO_TASK,
    SELECT_TODO_LIST,
    DELETE_TODO_TASK,
)
from config import DB_PATH

def connect_db():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def initialize_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_TASKS_TABLE)
        cursor.execute(CREATE_TODO_TABLE)
        conn.commit()

def log_task(task_name, start_time, initial_duration, end_time, actual_duration, completed):
    with connect_db() as conn:
        cursor = conn.cursor()
        status = "Finished" if completed else "Not Finished"
        cursor.execute(
            INSERT_TASK,
            (
                task_name,
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                initial_duration,
                actual_duration,
                status,
            ),
        )
        conn.commit()

def add_task_to_todo(task_name, duration):
    with connect_db() as conn:
        cursor = conn.cursor()
        added_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(INSERT_TODO_TASK, (task_name, duration, added_date))
        conn.commit()

def fetch_todo_list():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(SELECT_TODO_LIST)
        rows = cursor.fetchall()
        todo_list = [
            Todo(
                task_name=row[0],
                duration=row[1],
                added_date=datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            )
            for row in rows
        ]
        return todo_list

def delete_todo_task(task_name):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(DELETE_TODO_TASK, (task_name,))
        conn.commit()

def fetch_task_history():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(SELECT_TASK_HISTORY)
        rows = cursor.fetchall()
        task_history = [
            Task(
                task_name=row[0],
                start_time=datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"),
                end_time=datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S"),
                initial_duration=row[3],
                actual_duration=row[4],
                status=row[5],
            )
            for row in rows
        ]
        return task_history
