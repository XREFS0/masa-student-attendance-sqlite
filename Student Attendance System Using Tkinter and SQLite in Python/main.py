"""
Developed by MASA
All Rights Reserved.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DB_FILE = "attendance.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT UNIQUE
    )
    """)

    c.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in c.fetchall()]
    if "section" not in columns:
        c.execute("ALTER TABLE students ADD COLUMN section TEXT NOT NULL DEFAULT 'A'")

    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        subject TEXT NOT NULL DEFAULT 'General',
        status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
        UNIQUE(student_id, date, subject),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


def add_student(name, roll, section):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO students (name, roll, section) VALUES (?, ?, ?)", (name, roll, section))
        conn.commit()
        messagebox.showinfo("Success", f"Student '{name}' added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Roll number '{roll}' already exists.")
    finally:
        conn.close()


def mark_attendance(student_id, date_str, subject, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO attendance (student_id, date, subject, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, date, subject)
            DO UPDATE SET status=excluded.status
        """,
            (student_id, date_str, subject, status),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_students():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()
    return data


def fetch_attendance(date_filter=None, section_filter=None, subject_filter=None, sort_by="date"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    query = """
        SELECT s.roll, s.name, s.section, a.date, a.subject, a.status
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        WHERE 1=1
    """
    params = []
    if date_filter:
        query += " AND a.date = ?"
        params.append(date_filter)
    if section_filter:
        query += " AND s.section = ?"
        params.append(section_filter)
    if subject_filter:
        query += " AND a.subject = ?"
        params.append(subject_filter)

    if sort_by == "name":
        query += " ORDER BY s.name ASC"
    elif sort_by == "roll":
        query += " ORDER BY s.roll ASC"
    elif sort_by == "section":
        query += " ORDER BY s.section ASC"
    elif sort_by == "subject":
        query += " ORDER BY a.subject ASC"
    else:
        query += " ORDER BY a.date DESC"

    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data


def add_student_window():
    win = tk.Toplevel(root)
    win.title("MASA - Add Student")
    win.geometry("350x350")
    win.resizable(False, False)
    win.configure(bg="#f0f2f5")

    tk.Label(win, text="Add New Student", font=("Segoe UI", 13, "bold"), bg="#f0f2f5").pack(pady=10)
    tk.Label(win, text="Name:", bg="#f0f2f5", font=("Segoe UI", 11)).pack()
    name_entry = tk.Entry(win, font=("Segoe UI", 12))
    name_entry.pack(pady=5, ipadx=5, ipady=3)

    tk.Label(win, text="Roll No:", bg="#f0f2f5", font=("Segoe UI", 11)).pack()
    roll_entry = tk.Entry(win, font=("Segoe UI", 12))
    roll_entry.pack(pady=5, ipadx=5, ipady=3)

    tk.Label(win, text="Section:", bg="#f0f2f5", font=("Segoe UI", 11)).pack()
    section_entry = tk.Entry(win, font=("Segoe UI", 12))
    section_entry.pack(pady=5, ipadx=5, ipady=3)

    def save_student():
        name = name_entry.get().strip()
        roll = roll_entry.get().strip()
        section = section_entry.get().strip()
        if name and roll and section:
            add_student(name, roll, section)
            win.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    tk.Button(
        win,
        text="Save Student",
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        padx=10,
        pady=5,
        command=save_student,
    ).pack(pady=15)


def mark_attendance_window():
    win = tk.Toplevel(root)
    win.title("MASA - Mark Attendance")
    win.geometry("800x550")
    win.resizable(False, False)
    win.configure(bg="#f0f2f5")

    tk.Label(win, text="Mark Attendance", font=("Segoe UI", 14, "bold"), bg="#f0f2f5").pack(pady=10)

    filter_frame = tk.Frame(win, bg="#f0f2f5")
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Date (YYYY-MM-DD): ", bg="#f0f2f5", font=("Segoe UI", 11)).grid(
        row=0, column=0, padx=5
    )
    date_entry = tk.Entry(filter_frame, width=15, font=("Segoe UI", 12))
    date_entry.insert(0, str(date.today()))
    date_entry.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Section: ", bg="#f0f2f5", font=("Segoe UI", 11)).grid(
        row=0, column=2, padx=5
    )
    section_entry = tk.Entry(filter_frame, width=10, font=("Segoe UI", 12))
    section_entry.grid(row=0, column=3, padx=5)

    tk.Label(filter_frame, text="Subject: ", bg="#f0f2f5", font=("Segoe UI", 11)).grid(
        row=0, column=4, padx=5
    )
    subject_entry = tk.Entry(filter_frame, width=20, font=("Segoe UI", 12))
    subject_entry.grid(row=0, column=5, padx=5)

    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Roll", "Name", "Section", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)

    tree.tag_configure("oddrow", background="#e8f0fe")
    tree.tag_configure("evenrow", background="#ffffff")

    def load_students():
        date_str = date_entry.get().strip()
        section = section_entry.get().strip()
        subject = subject_entry.get().strip() or "General"
        for i in tree.get_children():
            tree.delete(i)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if section:
            c.execute("SELECT * FROM students WHERE section=? ORDER BY roll", (section,))
        else:
            c.execute("SELECT * FROM students ORDER BY roll")
        students = c.fetchall()
        conn.close()

        for i, s in enumerate(students):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "SELECT status FROM attendance WHERE student_id=? AND date=? AND subject=?",
                (s[0], date_str, subject),
            )
            result = c.fetchone()
            conn.close()
            status = result[0] if result else "Absent"
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=(s[2], s[1], s[3], status), tags=(tag,))

    tk.Button(
        win,
        text="Load Students",
        bg="#2196F3",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        padx=10,
        pady=5,
        command=load_students,
    ).pack(pady=5)

    def mark_selected(status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select at least one student.")
            return
        for sel in selected:
            tree.set(sel, column="Status", value=status)

    btn_frame = tk.Frame(win, bg="#f0f2f5")
    btn_frame.pack(pady=10)
    tk.Button(
        btn_frame,
        text="Mark Present",
        bg="#4CAF50",
        fg="white",
        width=15,
        command=lambda: mark_selected("Present"),
    ).pack(side="left", padx=10)
    tk.Button(
        btn_frame,
        text="Mark Absent",
        bg="#F44336",
        fg="white",
        width=15,
        command=lambda: mark_selected("Absent"),
    ).pack(side="left", padx=10)

    def save_attendance():
        date_str = date_entry.get().strip()
        subject = subject_entry.get().strip() or "General"
        for sel in tree.get_children():
            roll = tree.item(sel)["values"][0]
            section = tree.item(sel)["values"][2]
            status = tree.item(sel)["values"][3]
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id FROM students WHERE roll=? AND section=?", (roll, section))
            sid = c.fetchone()
            conn.close()
            if sid:
                mark_attendance(sid[0], date_str, subject, status)
        messagebox.showinfo("Success", "Attendance saved successfully!")

    tk.Button(
        win,
        text="Save Attendance",
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        width=20,
        pady=5,
        command=save_attendance,
    ).pack(pady=10)


def view_attendance_window():
    win = tk.Toplevel(root)
    win.title("MASA - View Attendance Records")
    win.geometry("900x500")
    win.resizable(False, False)
    win.configure(bg="#f0f2f5")

    tk.Label(win, text="View Attendance", font=("Segoe UI", 14, "bold"), bg="#f0f2f5").pack(pady=10)

    filter_frame = tk.Frame(win, bg="#f0f2f5")
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Date (YYYY-MM-DD): ", bg="#f0f2f5", font=("Segoe UI", 11)).pack(side=tk.LEFT)
    date_entry = tk.Entry(filter_frame, width=15, font=("Segoe UI", 12))
    date_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_frame, text="Section: ", bg="#f0f2f5", font=("Segoe UI", 11)).pack(side=tk.LEFT)
    section_entry = tk.Entry(filter_frame, width=10, font=("Segoe UI", 12))
    section_entry.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_frame, text="Subject: ", bg="#f0f2f5", font=("Segoe UI", 11)).pack(side=tk.LEFT)
    subject_entry = tk.Entry(filter_frame, width=15, font=("Segoe UI", 12))
    subject_entry.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Roll", "Name", "Section", "Date", "Subject", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)

    tree.tag_configure("oddrow", background="#e8f0fe")
    tree.tag_configure("evenrow", background="#ffffff")

    def load_data():
        date_filter = date_entry.get().strip()
        section_filter = section_entry.get().strip()
        subject_filter = subject_entry.get().strip()
        rows = fetch_attendance(
            date_filter if date_filter else None,
            section_filter if section_filter else None,
            subject_filter if subject_filter else None,
        )
        for i in tree.get_children():
            tree.delete(i)
        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=row, tags=(tag,))

    tk.Button(
        filter_frame,
        text="Search",
        width=12,
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        command=load_data,
    ).pack(side=tk.LEFT, padx=5)
    load_data()


root = tk.Tk()
root.title("MASA - Student Attendance System")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="#f0f2f5")

init_db()

tk.Label(root, text="Student Attendance System", font=("Segoe UI", 15, "bold"), bg="#f0f2f5").pack(pady=25)

btn_style = {"font": ("Segoe UI", 12, "bold"), "width": 25, "height": 2}

tk.Button(root, text="Add Student", bg="#2196F3", fg="white", **btn_style, command=add_student_window).pack(
    pady=8
)
tk.Button(
    root, text="Mark Attendance", bg="#4CAF50", fg="white", **btn_style, command=mark_attendance_window
).pack(pady=8)
tk.Button(
    root, text="View Attendance", bg="#FF9800", fg="white", **btn_style, command=view_attendance_window
).pack(pady=8)
tk.Button(root, text="Exit", bg="#F44336", fg="white", **btn_style, command=root.destroy).pack(pady=15)

root.mainloop()
