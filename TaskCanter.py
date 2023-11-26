import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
from datetime import datetime, timedelta

def create_table():
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def add_task():
    task = entry.get()
    priority = priority_var.get()
    due_date = due_date_var.get()

    if task:
        task_display = f"{task} - Priority: {priority} - Due Date: {due_date} - Not Completed"
        listbox.insert("", "end", values=(task, priority, due_date, "Not Completed"))
        save_task_to_database(task, priority, due_date, "Not Completed")
        set_deadline_notification(task, due_date)
        entry.delete(0, tk.END)
        priority_var.set("Low")
        due_date_var.set("")

def remove_task():
    selected_item = listbox.selection()
    if selected_item:
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to remove this task?")
        if confirmation:
            task_id = selected_item[0]
            remove_task_from_database(task_id)
            listbox.delete(selected_item)

def complete_task():
    selected_item = listbox.selection()
    if selected_item:
        task_id = selected_item[0]
        complete_task_in_database(task_id)
        task = listbox.item(selected_item, 'values')
        if task[3] == "Not Completed":
            updated_task_display = f"{task[0]} - Priority: {task[1]} - Due Date: {task[2]} - Completed"
            listbox.item(selected_item, values=(task[0], task[1], task[2], "Completed"))
            set_deadline_notification(task[0], task[2])

def save_tasks():
    tasks = listbox.get_children()
    with open("tasks.txt", "w") as file:
        for task_id in tasks:
            task_values = listbox.item(task_id, 'values')
            file.write(f"{task_values[0]} - Priority: {task_values[1]} - Due Date: {task_values[2]} - {task_values[3]}\n")
    messagebox.showinfo("Saved", "Tasks saved successfully!")

def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            tasks = [line.strip() for line in file.readlines()]
            listbox.delete(*listbox.get_children())
            for task in tasks:
                task_parts = task.split(" - ")
                listbox.insert("", "end", values=(task_parts[0], task_parts[2], task_parts[4], task_parts[6]))
        messagebox.showinfo("Loaded", "Tasks loaded successfully!")
    except FileNotFoundError:
        messagebox.showwarning("File Not Found", "No saved tasks found.")

def sort_tasks():
    tasks = listbox.get_children()
    tasks = sorted(tasks, key=lambda task_id: (listbox.item(task_id, 'values')[3], listbox.item(task_id, 'values')[1]))
    listbox.delete(*listbox.get_children())
    for task_id in tasks:
        task_values = listbox.item(task_id, 'values')
        listbox.insert("", "end", values=(task_values[0], task_values[1], task_values[2], task_values[3]))

def filter_tasks():
    selected_filter = filter_var.get()
    tasks = listbox.get_children()
    filtered_tasks = []

    if selected_filter == "All":
        filtered_tasks = tasks
    elif selected_filter == "Completed":
        filtered_tasks = [task_id for task_id in tasks if listbox.item(task_id, 'values')[3] == "Completed"]
    elif selected_filter == "Not Completed":
        filtered_tasks = [task_id for task_id in tasks if listbox.item(task_id, 'values')[3] == "Not Completed"]

    listbox.delete(*listbox.get_children())
    for task_id in filtered_tasks:
        task_values = listbox.item(task_id, 'values')
        listbox.insert("", "end", values=(task_values[0], task_values[1], task_values[2], task_values[3]))

def open_calendar():
    def set_due_date():
        due_date_var.set(cal.get_date())
        top.destroy()

    top = tk.Toplevel(root)
    cal = Calendar(top, selectmode="day", year=2023, month=11, day=26)
    cal.pack(padx=20, pady=20)
    set_button = tk.Button(top, text="Set Due Date", command=set_due_date)
    set_button.pack(pady=10)

def set_deadline_notification(task, due_date):
    try:
        due_date_object = datetime.strptime(due_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_until_due = (due_date_object - today).days

        if days_until_due >= 0:
            root.after(days_until_due * 86400000, show_notification, task, due_date)
    except ValueError:
        pass

def show_notification(task, due_date):
    messagebox.showinfo("Deadline Notification", f"The task '{task}' is due on {due_date}!")

def get_task_id(selected_item):
    return selected_item[0]

def save_task_to_database(task, priority, due_date, status):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tasks (task, priority, due_date, status) VALUES (?, ?, ?, ?)", (task, priority, due_date, status))
    connection.commit()
    connection.close()

def remove_task_from_database(task_id):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    connection.commit()
    connection.close()

def complete_task_in_database(task_id):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
    connection.commit()
    connection.close()

def edit_task():
    selected_item = listbox.selection()
    if selected_item:
        task_id = get_task_id(selected_item)
        top = tk.Toplevel(root)
        top.title("Edit Task")

        edited_task_var = tk.StringVar()
        edited_task_var.set(listbox.item(selected_item, 'values')[0])

        edited_task_label = tk.Label(top, text="Edit Task:")
        edited_task_label.pack()

        edited_task_entry = tk.Entry(top, textvariable=edited_task_var, width=30)
        edited_task_entry.pack(pady=10)

        priority_label = tk.Label(top, text="Priority:")
        priority_label.pack()

        edited_priority_var = tk.StringVar()
        edited_priority_var.set(listbox.item(selected_item, 'values')[1])

        priority_dropdown = tk.OptionMenu(top, edited_priority_var, "Low", "Medium", "High")
        priority_dropdown.pack()

        due_date_label = tk.Label(top, text="Due Date:")
        due_date_label.pack()

        edited_due_date_var = tk.StringVar()
        edited_due_date_var.set(listbox.item(selected_item, 'values')[2])

        edited_due_date_entry = tk.Entry(top, textvariable=edited_due_date_var, width=20)
        edited_due_date_entry.pack()

        save_changes_button = tk.Button(top, text="Save Changes", command=lambda: save_changes(task_id))
        save_changes_button.pack()

    def save_changes(task_id):
        edited_task = edited_task_var.get()
        edited_priority = edited_priority_var.get()
        edited_due_date = edited_due_date_var.get()

        if edited_task:
            updated_task_display = f"{edited_task} - Priority: {edited_priority} - Due Date: {edited_due_date} - {listbox.item(selected_item, 'values')[3]}"
            listbox.item(selected_item, values=(edited_task, edited_priority, edited_due_date, listbox.item(selected_item, 'values')[3]))

            connection = sqlite3.connect("tasks.db")
            cursor = connection.cursor()
            cursor.execute("UPDATE tasks SET task=?, priority=?, due_date=? WHERE id=?", (edited_task, edited_priority, edited_due_date, task_id))
            connection.commit()
            connection.close()

            top.destroy()

# Create the main window
root = tk.Tk()
root.title("Todo List App")

# Create and configure the task entry
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Create and configure the Priority dropdown
priority_var = tk.StringVar(root)
priority_var.set("Low")
priority_label = tk.Label(root, text="Priority:")
priority_label.pack()
priority_dropdown = tk.OptionMenu(root, priority_var, "Low", "Medium", "High")
priority_dropdown.pack()

# Create and configure the Due Date entry
due_date_var = tk.StringVar(root)
due_date_label = tk.Label(root, text="Due Date:")
due_date_label.pack()
due_date_entry = tk.Entry(root, textvariable=due_date_var, width=20)
due_date_entry.pack()

# Create and configure the Add Task button
add_button = tk.Button(root, text="Add Task", command=add_task)
add_button.pack()

# Create and configure the task treeview
columns = ("Task", "Priority", "Due Date", "Status")
listbox = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")

for col in columns:
    listbox.heading(col, text=col)
    listbox.column(col, width=120, anchor="center")

listbox.pack(pady=10)

# Create and configure the Remove Task button
remove_button = tk.Button(root, text="Remove Task", command=remove_task)
remove_button.pack()

# Create and configure the Complete Task button
complete_button = tk.Button(root, text="Complete Task", command=complete_task)
complete_button.pack()

# Create and configure the Save Tasks button
save_button = tk.Button(root, text="Save Tasks", command=save_tasks)
save_button.pack()

# Create and configure the Load Tasks button
load_button = tk.Button(root, text="Load Tasks", command=load_tasks)
load_button.pack()

# Create and configure the Sort Tasks button
sort_button = tk.Button(root, text="Sort Tasks", command=sort_tasks)
sort_button.pack()

# Create and configure the Filter Tasks dropdown
filter_var = tk.StringVar(root)
filter_var.set("All")
filter_label = tk.Label(root, text="Filter Tasks:")
filter_label.pack()
filter_dropdown = tk.OptionMenu(root, filter_var, "All", "Completed", "Not Completed")
filter_dropdown.pack()

# Create and configure the Filter Tasks button
filter_button = tk.Button(root, text="Filter Tasks", command=filter_tasks)
filter_button.pack()

# Create and configure the Open Calendar button
calendar_button = tk.Button(root, text="Open Calendar", command=open_calendar)
calendar_button.pack()

# Create and configure the Edit Task button
edit_button = tk.Button(root, text="Edit Task", command=edit_task)
edit_button.pack()

# Load tasks from the database on startup
create_table()
load_tasks()

# Start the main event loop
root.mainloop()
