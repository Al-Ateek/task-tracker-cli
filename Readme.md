# Task Tracker CLI

## A simple command-line task management application built with Python for learning and practicing CLI development, file handling, JSON persistence, and input validation.

## Project Page URL

<code>https://roadmap.sh/projects/task-tracker</code>

### What I learned

* Building CLI applications with <code>argparse</code>
* Reading and writing JSON files.
* File Handling
* Input validation and error handling
* Working with timestamps
* Using Git for version control

<hr>

### Features

* Add a task with its description.
* Update your task's description.
* Update your task's status.
* Delete an added task.
* List all your tasks or listing them by their status.

<hr>

### How to install

You just have to install python on your device, then you can run the task-cli.py script on your CMD/Terminal.

<hr>

### How to use

1. Add your first task:<br>
    <code> python3 task-cli.py add "Description" </code>

2. List your tasks:<br>
    <code> python3 task-cli.py list </code>
    <p> you can also add your filter like this (<code>python3 task-cli.py list done</code>)<br>
    You can choose on of these statuses <code>['done', 'in-progress', 'todo']</code>.</p>

3. Update a task using task id: <br>
    <code>python3 task-cli.py update 1 "update task"</code>

4. Update a task's status:<br>
    <code>python3 task-cli.py mark-in-progress {id}</code><br>
    <code>python3 task-cli.py mark-done {id}</code>

5. Delete a task using its id: <br>
    <code>python3 task-cli.py delete 1</code>