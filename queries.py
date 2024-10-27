# queries.py

CREATE_TASKS_TABLE = '''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    task_name TEXT,
    start_time TEXT,
    end_time TEXT,
    initial_duration INTEGER,
    actual_duration INTEGER,
    status TEXT
)
'''

INSERT_TASK = '''
INSERT INTO tasks (task_name, start_time, end_time, initial_duration, actual_duration, status)
VALUES (?, ?, ?, ?, ?, ?)
'''

# Updated to include 'id'
SELECT_TASK_HISTORY = '''
SELECT id, task_name, start_time, end_time, initial_duration, actual_duration, status FROM tasks
'''

# New query to delete a task by ID
DELETE_TASK = '''
DELETE FROM tasks WHERE id = ?
'''

# Existing queries for todo functionality
CREATE_TODO_TABLE = '''
CREATE TABLE IF NOT EXISTS todo (
    id INTEGER PRIMARY KEY,
    task_name TEXT,
    duration INTEGER,
    added_date TEXT
)
'''

INSERT_TODO_TASK = '''
INSERT INTO todo (task_name, duration, added_date) VALUES (?, ?, ?)
'''

SELECT_TODO_LIST = '''
SELECT task_name, duration, added_date FROM todo
'''

DELETE_TODO_TASK = '''
DELETE FROM todo WHERE task_name = ?
'''