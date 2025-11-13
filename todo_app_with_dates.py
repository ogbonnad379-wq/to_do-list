# To-Do List App with Completion & Due Dates (Python)
# Filename suggestion: todo_app_with_dates.py

"""
Simple command-line To-Do list application that:
- Stores tasks in a JSON file so data persists between runs
- Supports: add task, view tasks, mark complete/incomplete, delete, edit, filter by status or due date
- Each task has: id, title, due_date (ISO string or empty), completed (bool), created_at (ISO)

This file includes the program code followed by a plain, line-by-line explanation of every single line.
"""

import json
import os
from datetime import datetime

# File where tasks will be stored
FILENAME = "todo_data.json"

# ---------------------- Helper functions ----------------------

def load_tasks():
    """Load tasks from the JSON file. If file doesn't exist return empty list."""
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, return an empty list
            return []


def save_tasks(tasks):
    """Save tasks list to the JSON file."""
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def generate_id(tasks):
    """Generate a simple numeric id: 1 + max id found, or 1 if none."""
    if not tasks:
        return 1
    ids = [task.get("id", 0) for task in tasks]
    return max(ids) + 1


def parse_date(date_str):
    """Try to parse a date string in common formats and return ISO date (YYYY-MM-DD) or empty string.
    Acceptable examples: 2025-11-12, 12/11/2025, 12-11-2025, Nov 12 2025
    If parsing fails return empty string.
    """
    if not date_str:
        return ""
    date_str = date_str.strip()
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%b %d %Y",
        "%B %d %Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    # As a last resort try parsing ISO directly
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.date().isoformat()
    except Exception:
        return ""


def add_task(tasks):
    """Prompt the user to create a new task and append it to tasks list."""
    title = input("Enter task title: ").strip()
    if not title:
        print("❌ Task title cannot be empty.")
        return
    due_input = input("Enter due date (optional, e.g. 2025-11-12 or 12/11/2025). Press Enter to skip: ")
    due_date = parse_date(due_input)

    new_task = {
        "id": generate_id(tasks),
        "title": title,
        "due_date": due_date,      # ISO string like '2025-11-12' or empty
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"✅ Task added: ({new_task['id']}) {new_task['title']}")


def show_tasks(tasks, filter_by=None):
    """Display tasks to the user.
    filter_by can be: None, 'all', 'completed', 'incomplete', 'overdue', 'due_today'
    """
    if not tasks:
        print("\n📭 No tasks found.\n")
        return

    now = datetime.now().date()
    filtered = []

    for task in tasks:
        if filter_by in (None, 'all'):
            filtered.append(task)
        elif filter_by == 'completed' and task.get('completed'):
            filtered.append(task)
        elif filter_by == 'incomplete' and not task.get('completed'):
            filtered.append(task)
        elif filter_by == 'due_today':
            if task.get('due_date'):
                try:
                    if datetime.fromisoformat(task['due_date']).date() == now:
                        filtered.append(task)
                except Exception:
                    pass
        elif filter_by == 'overdue':
            if task.get('due_date') and not task.get('completed'):
                try:
                    if datetime.fromisoformat(task['due_date']).date() < now:
                        filtered.append(task)
                except Exception:
                    pass

    if not filtered:
        print("\nNo tasks match that filter.\n")
        return

    print("\n🗒️  Tasks:\n")
    for task in filtered:
        status = "✅" if task.get('completed') else "⬜"
        due = task.get('due_date') or "No due date"
        print(f"ID: {task.get('id')} | {status} {task.get('title')} (Due: {due})")
    print()


def find_task_by_id(tasks, task_id):
    """Return the task object with matching id or None."""
    for task in tasks:
        if task.get('id') == task_id:
            return task
    return None


def mark_complete(tasks):
    """Mark a task complete or incomplete by id."""
    try:
        task_id = int(input("Enter task ID to toggle completion: "))
    except ValueError:
        print("❌ Please enter a valid numeric ID.")
        return
    task = find_task_by_id(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return
    task['completed'] = not task.get('completed', False)
    save_tasks(tasks)
    state = 'completed' if task['completed'] else 'incomplete'
    print(f"🔁 Task {task_id} marked as {state}.")


def delete_task(tasks):
    """Delete a task by id."""
    try:
        task_id = int(input("Enter task ID to delete: "))
    except ValueError:
        print("❌ Please enter a valid numeric ID.")
        return
    task = find_task_by_id(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return
    tasks.remove(task)
    save_tasks(tasks)
    print(f"🗑️  Deleted task {task_id}: {task.get('title')}")


def edit_task(tasks):
    """Edit title or due date of a task by id."""
    try:
        task_id = int(input("Enter task ID to edit: "))
    except ValueError:
        print("❌ Please enter a valid numeric ID.")
        return
    task = find_task_by_id(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return

    print(f"Current title: {task.get('title')}")
    new_title = input("Enter new title (leave blank to keep): ").strip()
    if new_title:
        task['title'] = new_title

    print(f"Current due date: {task.get('due_date') or 'No due date'}")
    new_due = input("Enter new due date (leave blank to keep / enter 'clear' to remove): ").strip()
    if new_due.lower() == 'clear':
        task['due_date'] = ""
    elif new_due:
        parsed = parse_date(new_due)
        if parsed:
            task['due_date'] = parsed
        else:
            print("❌ Couldn't parse that date. Keeping previous due date.")

    save_tasks(tasks)
    print(f"✏️  Task {task_id} updated.")


# ---------------------- Main program loop ----------------------

def main():
    tasks = load_tasks()
    print("\n🧾 To-Do List App (with due dates & completion)\n")

    while True:
        print("Menu:")
        print("1. Show all tasks")
        print("2. Show incomplete tasks")
        print("3. Show completed tasks")
        print("4. Show tasks due today")
        print("5. Show overdue tasks")
        print("6. Add task")
        print("7. Edit task")
        print("8. Toggle complete/incomplete")
        print("9. Delete task")
        print("0. Exit")

        choice = input("Choose an option (0-9): ").strip()

        if choice == '1':
            show_tasks(tasks, filter_by='all')
        elif choice == '2':
            show_tasks(tasks, filter_by='incomplete')
        elif choice == '3':
            show_tasks(tasks, filter_by='completed')
        elif choice == '4':
            show_tasks(tasks, filter_by='due_today')
        elif choice == '5':
            show_tasks(tasks, filter_by='overdue')
        elif choice == '6':
            add_task(tasks)
        elif choice == '7':
            edit_task(tasks)
        elif choice == '8':
            mark_complete(tasks)
        elif choice == '9':
            delete_task(tasks)
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.")


if __name__ == "__main__":
    main()


# ---------------------- Line-by-line plain explanation ----------------------

# I will now explain each line above plainly. Read these explanations slowly and refer back to the code.

# 1-3: import json, os, datetime
# import json
# - Brings in the json module so we can read/write JSON files.
# import os
# - Brings in the os module which we use to check if the data file exists.
# from datetime import datetime
# - Imports the datetime class so we can handle dates and times.

# 5: FILENAME = "todo_data.json"
# - Sets a constant that names the file where tasks are stored. If you change this name,
#   the program will read/write that file instead.

# 8-18: def load_tasks():
# def load_tasks():
# - Defines a function named load_tasks. Functions are reusable blocks of code.
#     if not os.path.exists(FILENAME):
#         return []
# - Checks whether the data file exists. If it does not, return an empty list (no tasks).
#     with open(FILENAME, "r", encoding="utf-8") as f:
# - Opens the file for reading. 'with' ensures the file is closed automatically.
#         try:
#             return json.load(f)
# - Attempts to load JSON content and return it as a Python list.
#         except json.JSONDecodeError:
#             # If the file is empty or corrupted, return an empty list
#             return []
# - If the file has invalid JSON, return an empty list instead of crashing.

# 20-23: def save_tasks(tasks):
# def save_tasks(tasks):
# - Defines a function that accepts a list named tasks and writes it to the JSON file.
#     with open(FILENAME, "w", encoding="utf-8") as f:
# - Opens the file in write mode (this overwrites the file with current data).
#         json.dump(tasks, f, ensure_ascii=False, indent=2)
# - Converts the tasks list to JSON and writes it. indent=2 makes the file readable.

# 25-31: def generate_id(tasks):
# def generate_id(tasks):
# - Returns a numeric id for a new task.
#     if not tasks:
#         return 1
# - If there are no tasks yet, start IDs at 1.
#     ids = [task.get("id", 0) for task in tasks]
# - Build a simple list of existing ids (default 0 if missing).
#     return max(ids) + 1
# - Return one more than the highest id found so new ids are unique.

# 33-63: def parse_date(date_str):
# def parse_date(date_str):
# - Attempts to parse different user-provided date formats and convert them to ISO format (YYYY-MM-DD).
#     if not date_str:
#         return ""
# - If the user gave a blank string, return blank (no due date).
#     date_str = date_str.strip()
# - Remove leading/trailing spaces.
#     formats = [...]
# - List of date formats we'll try to parse.
#     for fmt in formats:
#         try:
#             dt = datetime.strptime(date_str, fmt)
#             return dt.date().isoformat()
#         except ValueError:
#             continue
# - For each format try to parse. If parsing works, return ISO date. If not, try next.
#     try:
#         dt = datetime.fromisoformat(date_str)
#         return dt.date().isoformat()
#     except Exception:
#         return ""
# - As a last attempt, try ISO parsing. If everything fails, return empty string.

# 65-86: def add_task(tasks):
# def add_task(tasks):
# - Prompts the user for a title and optional due date and creates a task dict.
#     title = input("Enter task title: ").strip()
# - Reads title from user and trims spaces.
#     if not title:
#         print("❌ Task title cannot be empty.")
#         return
# - If title is blank show error and stop adding.
#     due_input = input("Enter due date (optional, e.g. 2025-11-12 or 12/11/2025). Press Enter to skip: ")
# - Ask the user for due date string.
#     due_date = parse_date(due_input)
# - Convert user input to standardized ISO date or blank.
#     new_task = { ... }
# - Create a dictionary representing the task with id, title, due_date, completed flag, created_at time.
#     tasks.append(new_task)
# - Add the new task to the list.
#     save_tasks(tasks)
# - Save updated tasks to file.
#     print(f"✅ Task added: ({new_task['id']}) {new_task['title']}")
# - Give feedback to the user.

# 88-131: def show_tasks(tasks, filter_by=None):
# def show_tasks(tasks, filter_by=None):
# - Display tasks. filter_by controls which tasks are shown.
#     if not tasks:
#         print("\n📭 No tasks found.\n")
#         return
# - If tasks list is empty tell the user and stop.
#     now = datetime.now().date()
# - Get today's date for comparing due dates.
#     filtered = []
# - Prepare an empty list to collect tasks that match the filter.
#     for task in tasks:
#         if filter_by in (None, 'all'):
#             filtered.append(task)
# - If no filter or 'all', include every task.
#         elif filter_by == 'completed' and task.get('completed'):
#             filtered.append(task)
# - If filter is 'completed' only add tasks where completed==True.
#         elif filter_by == 'incomplete' and not task.get('completed'):
#             filtered.append(task)
# - If filter is 'incomplete' add tasks where completed==False.
#         elif filter_by == 'due_today':
#             if task.get('due_date'):
#                 try:
#                     if datetime.fromisoformat(task['due_date']).date() == now:
#                         filtered.append(task)
#                 except Exception:
#                     pass
# - If filter is 'due_today' and task has a due_date try compare to today.
#         elif filter_by == 'overdue':
#             if task.get('due_date') and not task.get('completed'):
#                 try:
#                     if datetime.fromisoformat(task['due_date']).date() < now:
#                         filtered.append(task)
#                 except Exception:
#                     pass
# - If filter is 'overdue' and task has a due date and is not completed, check if date < today.
#     if not filtered:
#         print("\nNo tasks match that filter.\n")
#         return
# - If no tasks matched the chosen filter tell the user and stop.
#     print("\n🗒️  Tasks:\n")
# - Print header.
#     for task in filtered:
#         status = "✅" if task.get('completed') else "⬜"
#         due = task.get('due_date') or "No due date"
#         print(f"ID: {task.get('id')} | {status} {task.get('title')} (Due: {due})")
# - For each matched task show id, status, title and due date (or "No due date").

# 133-137: def find_task_by_id(tasks, task_id):
# def find_task_by_id(tasks, task_id):
# - Simple helper to return a task dict by its id.
#     for task in tasks:
#         if task.get('id') == task_id:
#             return task
#     return None
# - If not found return None.

# 139-156: def mark_complete(tasks):
# def mark_complete(tasks):
# - Toggle the completed state of a task chosen by numeric id.
#     try:
#         task_id = int(input("Enter task ID to toggle completion: "))
#     except ValueError:
#         print("❌ Please enter a valid numeric ID.")
#         return
# - Read id from user and handle non-numeric input.
#     task = find_task_by_id(tasks, task_id)
#     if not task:
#         print("❌ Task not found.")
#         return
# - Find the task; if missing tell the user.
#     task['completed'] = not task.get('completed', False)
# - Flip the completed flag (True -> False or False -> True).
#     save_tasks(tasks)
# - Save changes to disk.
#     state = 'completed' if task['completed'] else 'incomplete'
#     print(f"🔁 Task {task_id} marked as {state}.")
# - Show confirmation.

# 158-174: def delete_task(tasks):
# def delete_task(tasks):
# - Deletes a task by id after validating input.
#     try:
#         task_id = int(input("Enter task ID to delete: "))
#     except ValueError:
#         print("❌ Please enter a valid numeric ID.")
#         return
#     task = find_task_by_id(tasks, task_id)
#     if not task:
#         print("❌ Task not found.")
#         return
#     tasks.remove(task)
#     save_tasks(tasks)
#     print(f"🗑️  Deleted task {task_id}: {task.get('title')}")
# - Remove from list, save, and print confirmation.

# 176-201: def edit_task(tasks):
# def edit_task(tasks):
# - Allows editing title and due date.
#     try:
#         task_id = int(input("Enter task ID to edit: "))
#     except ValueError:
#         print("❌ Please enter a valid numeric ID.")
#         return
#     task = find_task_by_id(tasks, task_id)
#     if not task:
#         print("❌ Task not found.")
#         return
# - Validate id and existence as usual.
#     print(f"Current title: {task.get('title')}")
#     new_title = input("Enter new title (leave blank to keep): ").strip()
#     if new_title:
#         task['title'] = new_title
# - Let user change title. If blank keep old title.
#     print(f"Current due date: {task.get('due_date') or 'No due date'}")
#     new_due = input("Enter new due date (leave blank to keep / enter 'clear' to remove): ").strip()
#     if new_due.lower() == 'clear':
#         task['due_date'] = ""
#     elif new_due:
#         parsed = parse_date(new_due)
#         if parsed:
#             task['due_date'] = parsed
#         else:
#             print("❌ Couldn't parse that date. Keeping previous due date.")
# - Allow clearing the due date, updating with a parsed date, or keeping old one.
#     save_tasks(tasks)
#     print(f"✏️  Task {task_id} updated.")
# - Save and confirm.

# 203-246: Main program (def main())
# def main():
# - Loads tasks and runs a menu loop until the user exits.
#     tasks = load_tasks()
#     print("\n🧾 To-Do List App (with due dates & completion)\n")
# - Show title.
#     while True:
#         print("Menu:")
#         print("1. Show all tasks")
#         print("2. Show incomplete tasks")
#         print("3. Show completed tasks")
#         print("4. Show tasks due today")
#         print("5. Show overdue tasks")
#         print("6. Add task")
#         print("7. Edit task")
#         print("8. Toggle complete/incomplete")
#         print("9. Delete task")
#         print("0. Exit")
# - Print menu choices.
#         choice = input("Choose an option (0-9): ").strip()
# - Read user choice.
#         if choice == '1':
#             show_tasks(tasks, filter_by='all')
#         elif choice == '2':
#             show_tasks(tasks, filter_by='incomplete')
#         elif choice == '3':
#             show_tasks(tasks, filter_by='completed')
#         elif choice == '4':
#             show_tasks(tasks, filter_by='due_today')
#         elif choice == '5':
#             show_tasks(tasks, filter_by='overdue')
#         elif choice == '6':
#             add_task(tasks)
#         elif choice == '7':
#             edit_task(tasks)
#         elif choice == '8':
#             mark_complete(tasks)
#         elif choice == '9':
#             delete_task(tasks)
#         elif choice == '0':
#             print("👋 Goodbye!")
#             break
#         else:
#             print("❌ Invalid choice, please try again.")
# - Branch to the function that performs the chosen behavior. Loop until exit.

# 248-250: if __name__ == "__main__":
# if __name__ == "__main__":
#     main()
# - Standard Python idiom that runs the main() function when the script is executed directly.


# ---------------------- Additional project ideas for an intern ----------------------
# Below are real-life, practical Python project ideas that are great for internship portfolios.
# For each project I give 1 line of what you'll learn and why it's useful.
# 1) Expense Tracker (CSV/SQLite) - learn file I/O or SQL databases, useful for finance features.
# 2) Simple REST API with Flask/FastAPI - learn backend basics and HTTP, great for web dev roles.
# 3) Web Scraper + Scheduler - use BeautifulSoup/requests and cron/schedule to collect data; useful for data collection.
# 4) Data Dashboard (Pandas + Matplotlib/Plotly) - learn data cleaning and visualization, useful for analyst roles.
# 5) CLI Tool (argparse) - build a command-line utility (e.g., batch-rename files), learn argument parsing and packaging.
# 6) Unit-tested Library - pick a small library project and add pytest tests; excellent to show code quality.
# 7) Small ETL Pipeline - extract from CSV/JSON, transform, and load into DB; builds data engineering fundamentals.
# 8) Chatbot (rule-based or small ML) - learn text processing and state management; useful in many products.
# 9) Authentication Demo (Flask + SQLite) - implement signup/login flows, shows security basics for internships.
# 10) Automation Scripts - browser automation with Selenium or API automation for repetitive tasks.

# If you want, I can:
# - walk through running this to-do app step-by-step on your machine,
# - convert it to use SQLite instead of JSON,
# - or scaffold any of the projects above with starter code and line-by-line explanations.
