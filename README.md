
# TaskStrike - Terminal Productivity Timer

TaskStrike is a terminal-based Pomodoro timer with task tracking and to-do list management. Built for developers who love productivity tools, TaskStrike leverages SQLite for persistent data storage and provides cross-platform notifications to keep you focused.

## Features

- **Pomodoro-style Timer**: Track tasks with a countdown timer for focused work sessions.
- **Task History**: Logs completed tasks with details like start time, end time, and duration.
- **To-Do List**: Add tasks to a to-do list with custom durations for future work sessions.
- **Cross-Platform Notifications**: Receive alerts when a task’s time is up.
- **Customizable Configuration**: Settings like default task duration and notification preferences can be customized in a `.toml` file.

## Installation

### Prerequisites

- **Python 3.7+**
- **SQLite** (comes pre-installed with Python)

### Clone the Repository

```sh
git clone https://github.com/ddcodepl/task-strike
cd taskstrike
```

### Install Dependencies

Install the required Python packages listed in `requirements.txt`:

```sh
pip install -r requirements.txt
```

### Configuration

1. **Edit config.toml**: Customize settings for default task duration, database path, and notification preferences.

    ```toml
    [settings]
    default_duration = 25       # Default task duration in minutes
    db_path = "task_manager.db" # Path to SQLite database

    [notifications]
    enable = true               # Enable or disable notifications
    ```

2. **Database Initialization**: The database will initialize automatically the first time you run TaskStrike, creating tables for tasks and the to-do list.

## Usage

### Basic Commands

Run TaskStrike with these options:

1. **Start a Timer**:

    ```sh
    python main.py "Task Name" 25
    ```

    Starts a 25-minute timer for the specified task. Customize the duration as needed.

2. **Add a Task to the To-Do List**:

    ```sh
    python main.py --add-task -a "Task Name" 15
    ```

    Adds a task to the to-do list with a 15-minute duration for future tracking.

3. **View To-Do List**:

    ```sh
    python main.py --show-todo
    ```

4. **View Task History**:

    ```sh
    python main.py --show-history
    ```

### Optional Arguments

- `--add-task`: Adds a task to the to-do list with the specified name and duration.
- `--show-todo`: Displays all tasks in the to-do list.
- `--show-history`: Shows the task history in a formatted table.

### Example Usage

```sh
python main.py "Write Report" 30         # Starts a 30-minute timer for "Write Report"
python main.py --add-task "Review PR" 20 # Adds "Review PR" to the to-do list with a 20-minute duration
python main.py --show-todo               # Displays all to-do tasks
python main.py --show-history            # Displays the task history
```

## Project Structure

```plaintext
taskstrike/
├── config.toml       # Configuration file for customizable settings
├── db.py             # Database operations (CRUD operations and connection handling)
├── main.py           # Main application logic and command-line interface
├── models.py         # Data models for Task and To-Do list items
├── queries.py        # SQL queries for creating and manipulating tables
├── requirements.txt  # List of required packages
└── utils.py          # Utility functions for notifications and formatting
```

## Contributing

We welcome contributions! Here’s how to get involved:

1. **Fork the Repository**: Create a fork of the project on GitHub.
2. **Create a New Branch**: Use a descriptive branch name (e.g., `feature/task-tagging`).
3. **Make Changes**: Implement your changes, add tests if necessary.
4. **Run Tests**: Ensure that your code works as expected.
5. **Submit a Pull Request**: Open a pull request on GitHub with a description of your changes.

## Code of Conduct

We expect all contributors to adhere to our Code of Conduct for a respectful and collaborative environment.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Happy timing and productive work with TaskStrike!
