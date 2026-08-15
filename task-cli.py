import json
import os
import sys
from datetime import datetime
import argparse

TASK_FILE = "tasks.json"
REQUIRED_KEYS = {"id", "status", "updated_at", "created_at", "description"}
VALID_STATUS = {"done", "in-progress", "todo"}


if not os.path.exists(TASK_FILE):
    try:
        with open(TASK_FILE, "w") as file:
            json.dump([], file, indent=4)
    except OSError as e:
        print(f"Error: Could not create task file - {e}.", file=sys.stderr)
        sys.exit(1)


def validate_task(task, index):
    """Validate a single task object loaded from the tasks.json file.
    Checks that all required keys exist, that value types are correct, and that
    the status is one of the accepted values. Strips any unrecognised keys.
    Returns the cleaned task dict, or None if the task is too broken to use."""

    if not isinstance(task, dict):
        print(
            f"Warning: Task at position {index} is not an object - it's skipped.",
            file=sys.stderr,
        )
        return None

    missing = REQUIRED_KEYS - task.keys()
    if missing:
        print(
            f"Warning: Task at position {index} is missing keys {missing} - it's skipped.",
            file=sys.stderr,
        )
        return None

    if not isinstance(task["id"], int) or task["id"] <= 0:
        print(
            f"Warning: Task at position {index} has an invalid id - it's skipped.",
            file=sys.stderr,
        )
        return None

    if not isinstance(task["description"], str) or not task["description"].strip():
        print(
            f"Warning: Task at position {index} has an invalid 'description' - it's skipped.",
            file=sys.stderr,
        )
        return None

    if task["status"] not in VALID_STATUS:
        print(
            f"Warning: Task at position {index} has an invalid 'status' ('{task['status']}') - it's skipped",
            file=sys.stderr,
        )
        return None

    for date_key in ("created_at", "updated_at"):
        try:
            datetime.fromisoformat(task[date_key])
        except (ValueError, TypeError):
            print(
                f"Warning: Task at position {index} has an invalid '{date_key}' ('{task[date_key]}') - it's skipped.",
                file=sys.stderr,
            )
            return None

    return {key: task[key] for key in REQUIRED_KEYS}


def load_tasks():
    """Load and return the list of tasks from the JSON file.
    Returns an empty list if the file doesn't exist or contains invalid JSON."""
    if not os.path.exists(TASK_FILE):
        return []
    try:
        with open(TASK_FILE, "r") as file:
            valid_data = []
            data = json.load(file)
            if not isinstance(data, list):
                print(
                    "Error: tasks.json is corrupted (expected a list). Starting fresh.",
                    file=sys.stderr,
                )
                return []
            for i, task in enumerate(data):
                valid_task = validate_task(task, i)
                if valid_task is not None:
                    valid_data.append(valid_task)
            return valid_data
    except json.JSONDecodeError:
        print(
            "Error: tasks.json contains invalid JSON. Starting fresh.", file=sys.stderr
        )
        return []
    except OSError as e:
        print(f"Error: Could not read task file - {e}", file=sys.stderr)
        sys.exit(1)


def save_tasks(tasks):
    """Persist the current list of tasks to the JSON file, overwriting any previous content."""
    try:
        with open(TASK_FILE, "w") as file:
            json.dump(tasks, file, indent=4)
    except OSError as e:
        print(f"Error: Could not save tasks - {e}", file=sys.stderr)
        sys.exit(1)


def id_generator(tasks):
    """Generate and return the next available task ID based on the highest existing ID in the list."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def current_time():
    """Return the current local time as an ISO 8601 formatted string."""
    return datetime.now().isoformat()


def add_task(tasks, description):
    """Create a new task with the given description, assign it an ID and timestamps, and append it to the task list."""
    description = description.strip()
    if description == "":
        print("Error: Description cannot be empty.", file=sys.stderr)
        return
    new_id = id_generator(tasks)
    cur_time = current_time()
    task = {
        "id": new_id,
        "description": description,
        "status": "todo",
        "created_at": cur_time,
        "updated_at": cur_time,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {new_id}).")


def find_task(tasks, task_id):
    """Search the task list for a task matching the given ID.
    Returns its index if found, or -1 if not found."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return i
    return -1


def update_task(tasks, task_id, description):
    """Find a task by ID and update its description and updated timestamp.
    Prints an error to stderr if the ID doesn't exist."""
    description = description.strip()
    if description == "":
        print("Error: Description cannot be empty.", file=sys.stderr)
        return
    index = find_task(tasks, task_id)
    if index != -1:
        tasks[index]["description"] = description
        tasks[index]["updated_at"] = current_time()
        save_tasks(tasks)
        return
    print(f"Error: No task found with ID {task_id}.", file=sys.stderr)


def delete_task(tasks, task_id):
    """Find a task by ID and remove it from the list, then save.
    Prints an error to stderr if the ID doesn't exist."""
    index = find_task(tasks, task_id)
    if index != -1:
        del tasks[index]
        save_tasks(tasks)
        return
    print(f"Error: No task found with ID {task_id}.", file=sys.stderr)


def mark_task(tasks, task_id, status):
    """Find a task by ID and update its status and updated timestamp.
    Prints an error to stderr if the ID doesn't exist."""
    index = find_task(tasks, task_id)
    if index != -1:
        tasks[index]["status"] = status
        tasks[index]["updated_at"] = current_time()
        save_tasks(tasks)
        return
    print(f"Error: No task found with ID {task_id}.", file=sys.stderr)


def list_tasks(tasks, status_filter=None):
    """Print all tasks to the terminal.
    If status_filter is provided, only tasks matching that status are shown."""
    if not tasks:
        print("No tasks found.")
        return
    filter_tasks = tasks
    if status_filter is not None:
        filter_tasks = [task for task in tasks if task["status"] == status_filter]
    if not filter_tasks:
        print(f"No tasks found with status '{status_filter}'")
        return

    id_width = max(len(str(task["id"])) for task in filter_tasks)
    status_width = max(len(task["status"]) for task in filter_tasks)
    desc_width = max(len(task["description"]) for task in filter_tasks)
    date_width = max(
        max(len(task["created_at"]), len(task["updated_at"])) for task in filter_tasks
    )

    id_width = max(id_width, len("id"))
    status_width = max(status_width, len("status"))
    desc_width = max(desc_width, len("description"))
    date_width = max(date_width, len("created_at"))

    print(
        f"| {'ID':<{id_width}} | {'Status':<{status_width}} | {'Description':<{desc_width}} | {'Created':<{date_width}} | {'Updated':<{date_width}} |"
    )
    print(
        f"--{'-'*id_width}---{'-'*status_width}---{'-'*desc_width}---{'-'*date_width}---{'-'*date_width}--"
    )
    for task in filter_tasks:
        print(
            f"| {str(task['id']):<{id_width}} | "
            f"{task['status']:<{status_width}} | "
            f"{task['description']:<{desc_width}} | "
            f"{task['created_at']:<{date_width}} | "
            f"{task['updated_at']:<{date_width}} |"
        )


def positive_int(value):
    """Argparse type validator that rejects zero and negative integers."""
    try:
        int_value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer.")
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            f"ID must be a positive integer, got {int_value}."
        )
    return int_value


def main():
    """Entry point of the CLI.
    Parses command-line arguments and dispatches to the appropriate task function."""
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_add = subparsers.add_parser("add")
    parse_add.add_argument("description", type=str, help="Task description")

    parse_update = subparsers.add_parser("update")
    parse_update.add_argument("id", type=positive_int, help="Task ID")
    parse_update.add_argument("description", type=str, help="New description")

    parse_delete = subparsers.add_parser("delete")
    parse_delete.add_argument("id", type=positive_int, help="Task ID")

    parse_mip = subparsers.add_parser("mark-in-progress")
    parse_mip.add_argument("id", type=positive_int, help="Task ID")

    parse_done = subparsers.add_parser("mark-done")
    parse_done.add_argument("id", type=positive_int, help="Task ID")

    parse_list = subparsers.add_parser("list")
    parse_list.add_argument(
        "status",
        nargs="?",
        type=str,
        choices=["done", "in-progress", "todo"],
        help="Filter by status",
    )

    args = parser.parse_args()
    tasks = load_tasks()

    match args.command:
        case "add":
            add_task(tasks, args.description)
        case "update":
            update_task(tasks, args.id, args.description)
        case "delete":
            delete_task(tasks, args.id)
        case "mark-in-progress":
            mark_task(tasks, args.id, "in-progress")
        case "mark-done":
            mark_task(tasks, args.id, "done")
        case "list":
            list_tasks(tasks, args.status)


if __name__ == "__main__":
    main()
