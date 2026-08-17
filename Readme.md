# Task Tracker CLI  
  
A simple command-line task management application built with Python for learning  
and practicing CLI development, file handling, JSON persistence, and input validation.  
  
**Project page:** https://roadmap.sh/projects/task-tracker  
  
## What I learned  
  
- Building CLI applications with `argparse`  
- Reading and writing JSON files  
- File handling  
- Input validation and error handling  
- Working with timestamps  
- Using Git for version control  
  
## Features  
  
- Add a task with a description  
- Update a task's description  
- Update a task's status (`todo`, `in-progress`, `done`)  
- Delete a task  
- List all tasks, or filter them by status  
- Tasks are persisted to a local `tasks.json` file  
- Corrupted or invalid task entries are validated and skipped on load  
  
## Requirements  
  
- Python 3.10 or newer (the app uses the `match` statement)  
  
No third-party dependencies are needed — only the Python standard library.  
  
## Installation  
  
Make sure Python 3.10+ is installed, then run the `task-cli.py` script from your  
terminal / command prompt.  
  
## Usage  
  
1. Add a task:  
   ```  
   python3 task-cli.py add "Description"  
   ```  
  
2. List tasks:  
   ```  
   python3 task-cli.py list  
   ```  
   Optionally filter by status (`todo`, `in-progress`, `done`):  
   ```  
   python3 task-cli.py list done  
   ```  
  
3. Update a task's description by ID:  
   ```  
   python3 task-cli.py update 1 "Updated description"  
   ```  
  
4. Update a task's status:  
   ```  
   python3 task-cli.py mark-in-progress <id>  
   python3 task-cli.py mark-done <id>  
   ```  
  
5. Delete a task by ID:  
   ```  
   python3 task-cli.py delete 1  
   ```  
  
## Data storage  
  
Tasks are stored in `tasks.json` in the working directory. Each task contains an  
`id`, `description`, `status`, `created_at`, and `updated_at` field. The file is  
created automatically on first run.