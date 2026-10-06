from flask import Flask, request, render_template, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smart-attendance-secret-key"


# ==================== DATABASE ====================

def create_database():
    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==================== PASSWORD ====================

def add_password_column():
    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    try:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN password TEXT NOT NULL DEFAULT '12345'"
        )
        connection.commit()
        print("Password column added successfully!")

    except sqlite3.OperationalError:
        print("Password column already exists.")

    connection.close()


# ==================== TEST STUDENT ====================

def add_test_student():
    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (student_id, name, class_name)
            VALUES (?, ?, ?)
        """, (
            "STU001",
            "Anurag",
            "B.Tech CSE AI & ML - 2nd Year"
        ))

        connection.commit()
        print("Test student added successfully!")

    except sqlite3.IntegrityError:
        print("Student already exists.")

    connection.close()


# ==================== DATABASE SETUP ====================

create_database()
add_password_column()
add_test_student()


# ==================== HOME / STUDENT LOGIN ====================

@app.route("/")
def home():
    return render_template("student-login.html")


# ==================== STUDENT LOGIN ====================

@app.route("/student-login", methods=["POST"])
def student_login():

    data = request.get_json()

    student_id = data.get("student_id")
    password = data.get("password")

    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT student_id, name, class_name, password
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    connection.close()

    if student and student[3] == password:

        return {
            "success": True,
            "student_id": student[0],
            "name": student[1],
            "class_name": student[2]
        }

    return {
        "success": False,
        "message": "Invalid Student ID or Password"
    }


# ==================== STUDENT DASHBOARD ====================

@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student-dashboard.html")


# ==================== GENERATE QR ====================

@app.route("/generate-qr")
def generate_qr():
    return render_template("generate-qr.html")


# ==================== SCAN QR ====================

@app.route("/scan-qr")
def scan_qr():
    return render_template("scan-qr.html")


# ==================== MARK ATTENDANCE ====================

@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():

    data = request.get_json()

    student_id = data.get("student_id")

    if not student_id:
        return {
            "success": False,
            "message": "Student ID not found"
        }

    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT student_id FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        connection.close()

        return {
            "success": False,
            "message": "Student not found"
        }

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    subject = "QR Attendance"
    status = "Present"

    cursor.execute("""
        INSERT INTO attendance
        (student_id, subject, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        date,
        time,
        status
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Attendance marked successfully"
    }


# ==================== MY ATTENDANCE ====================

@app.route("/my-attendance")
def my_attendance():
    return render_template("my-attendance.html")


@app.route("/api/attendance/<student_id>")
def get_attendance(student_id):

    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT subject, date, time, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC, time DESC
    """, (student_id,))

    records = cursor.fetchall()

    connection.close()

    attendance = []

    for record in records:

        attendance.append({
            "subject": record[0],
            "date": record[1],
            "time": record[2],
            "status": record[3]
        })

    return attendance


# ==================== TEACHER LOGIN ====================

@app.route("/teacher-login", methods=["GET"])
def teacher_login_page():
    return render_template("teacher-login.html")


@app.route("/teacher-login", methods=["POST"])
def teacher_login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if email == "teacher@gmail.com" and password == "12345":

        session["teacher_logged_in"] = True

        return {
            "success": True,
            "message": "Teacher login successful"
        }

    return {
        "success": False,
        "message": "Invalid Teacher Email or Password"
    }


# ==================== TEACHER DASHBOARD ====================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")

    return render_template("teacher-Dashboard.html")


# ==================== TEACHER ATTENDANCE ====================

@app.route("/teacher-attendance")
def teacher_attendance():

    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")

    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT student_id, subject, date, time, status
        FROM attendance
        ORDER BY date DESC, time DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return render_template(
        "teacher-attendance.html",
        records=records
    )


# ==================== ATTENDANCE REPORT ====================

@app.route("/attendance-report")
def attendance_report():

    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")

    connection = sqlite3.connect("attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_id,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END),
            COUNT(*)
        FROM attendance
        GROUP BY student_id
    """)

    rows = cursor.fetchall()

    connection.close()

    reports = []

    for row in rows:

        student_id = row[0]
        present = row[1]
        total = row[2]

        percentage = round(
            (present / total) * 100, 2
        ) if total > 0 else 0

        reports.append(
            (student_id, present, total, percentage)
        )

    return render_template(
        "attendance-report.html",
        reports=reports
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/teacher-logout")
def teacher_logout():
    session.clear()
    return redirect("/teacher-login")


# ==================== START SERVER ====================

if __name__ == "__main__":
    app.run(debug=True)