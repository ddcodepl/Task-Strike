# models.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: int                    # Added task ID
    task_name: str
    start_time: datetime
    end_time: datetime
    initial_duration: int
    actual_duration: int
    status: str

@dataclass
class Todo:
    task_name: str
    duration: int
    added_date: datetime