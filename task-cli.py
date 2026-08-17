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
    """Validate and clean a single task object loaded from tasks.json.  
  
    Ensures the entry is a dict, contains all required keys, has correctly  
    typed values, a status within the accepted set, and parseable ISO 8601  
    timestamps. Any unrecognised keys are stripped from the returned dict.  
    A warning is printed to stderr for every rejected task.  
  
    Args:  
        task: The raw object read from the JSON file (expected to be a dict).  
        index (int): The position of the task in the file, used in warnings.  
  
    Returns:  
        dict | None: A cleaned task dict containing only the required keys,  
        or None if the task is invalid and should be skipped.  
    """  

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
    """Load, validate, and return the list of tasks from the JSON file.  
  
    Reads TASK_FILE, verifies the top-level structure is a list, and passes  
    each entry through validate_task so that malformed tasks are skipped.  
    Recoverable problems (missing file, invalid JSON, wrong structure) result  
    in an empty list; an unreadable file exits the program.  
  
    Returns:  
        list[dict]: The validated tasks. Empty if the file is missing,  
        contains invalid JSON, or is not a JSON list.  
  
    Raises:  
        SystemExit: If the file exists but cannot be read (OSError).  
    """
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
    """Write the list of tasks to the JSON file, overwriting existing content.  
  
    Args:  
        tasks (list[dict]): The tasks to persist.  
  
    Raises:  
        SystemExit: If the file cannot be written (OSError).  
    """  
    try:
        with open(TASK_FILE, "w") as file:
            json.dump(tasks, file, indent=4)
    except OSError as e:
        print(f"Error: Could not save tasks - {e}", file=sys.stderr)
        sys.exit(1)


def id_generator(tasks):
    """Compute the next available task ID.  
  
    Args:  
        tasks (list[dict]): The current list of tasks.  
  
    Returns:  
        int: 1 if the list is empty, otherwise one greater than the highest  
        existing task ID.  
    """  
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def current_time():
    """Return the current local time.  
  
    Returns:  
        str: The current local time as an ISO 8601 formatted string.  
    """  
    return datetime.now().isoformat()


def add_task(tasks, description):
    """Create a new task and append it to the task list, then save.  
  
    The description is stripped of surrounding whitespace and rejected if  
    empty. A new ID and identical created/updated timestamps are assigned,  
    and the task starts with status "todo".  
  
    Args:  
        tasks (list[dict]): The task list to append to (modified in place).  
        description (str): The description for the new task.  
    """  
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
    """Locate a task by its ID.  
  
    Args:  
        tasks (list[dict]): The task list to search.  
        task_id (int): The ID to look for.  
  
    Returns:  
        int: The index of the matching task, or -1 if no task has that ID.  
    """  
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return i
    return -1


def update_task(tasks, task_id, description):
    """Update the description of an existing task and refresh its timestamp.  
  
    The new description is stripped and rejected if empty. If no task matches  
    the given ID, an error is printed to stderr and nothing changes.  
  
    Args:  
        tasks (list[dict]): The task list (modified in place).  
        task_id (int): The ID of the task to update.  
        description (str): The new description.  
    """  
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
    """Remove a task by ID and save the updated list.  
  
    If no task matches the given ID, an error is printed to stderr and  
    nothing is removed.  
  
    Args:  
        tasks (list[dict]): The task list (modified in place).  
        task_id (int): The ID of the task to delete.  
    """  
    index = find_task(tasks, task_id)
    if index != -1:
        del tasks[index]
        save_tasks(tasks)
        return
    print(f"Error: No task found with ID {task_id}.", file=sys.stderr)


def mark_task(tasks, task_id, status):
    """Set the status of an existing task and refresh its timestamp.  
  
    If no task matches the given ID, an error is printed to stderr and  
    nothing changes.  
  
    Args:  
        tasks (list[dict]): The task list (modified in place).  
        task_id (int): The ID of the task to update.  
        status (str): The new status (e.g. "in-progress" or "done").  
    """  
    index = find_task(tasks, task_id)
    if index != -1:
        tasks[index]["status"] = status
        tasks[index]["updated_at"] = current_time()
        save_tasks(tasks)
        return
    print(f"Error: No task found with ID {task_id}.", file=sys.stderr)


def list_tasks(tasks, status_filter=None):
    """Print tasks to the terminal as a formatted, column-aligned table.  
  
    Column widths are computed dynamically from the data. If there are no  
    tasks, or none match the filter, an informational message is printed  
    instead of a table.  
  
    Args:  
        tasks (list[dict]): The tasks to display.  
        status_filter (str | None): If provided, only tasks whose status  
            equals this value are shown.  
    """  
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
    """Argparse type validator that accepts only positive integers.  
  
    Args:  
        value (str): The raw command-line argument.  
  
    Returns:  
        int: The parsed positive integer.  
  
    Raises:  
        argparse.ArgumentTypeError: If the value is not an integer or is  
            zero or negative.  
    """  
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
  
    Builds the argument parser with subcommands (add, update, delete,  
    mark-in-progress, mark-done, list), loads the current tasks, and  
    dispatches to the appropriate task function based on the chosen command.  
    """
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
