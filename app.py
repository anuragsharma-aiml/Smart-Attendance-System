from flask import Flask, request, render_template, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart-attendance-secret-key"
)

# ============================================================
# DATABASE PATH
# ============================================================

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/attendance.db"
else:
    DB_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "attendance.db"
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT '12345'
        )
    """)

    # Attendance table
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


# ============================================================
# PASSWORD COLUMN
# ============================================================

def add_password_column():

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN password TEXT NOT NULL DEFAULT '12345'
        """)

        connection.commit()
        print("Password column added successfully!")

    except sqlite3.OperationalError:
        # Column already exists
        pass

    connection.close()


# ============================================================
# TEST STUDENT
# ============================================================

def add_test_student():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO students
            (student_id, name, class_name, password)
            VALUES (?, ?, ?, ?)
        """, (
            "STU001",
            "Anurag",
            "B.Tech CSE AI & ML - 2nd Year",
            "12345"
        ))

        connection.commit()

        print("Test student added successfully!")

    except sqlite3.IntegrityError:

        print("Test student already exists.")

    connection.close()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:

    create_database()
    add_password_column()
    add_test_student()

    print("Database initialized successfully.")
    print("Database:", DB_PATH)

except Exception as error:

    print("DATABASE ERROR:", error)


# ============================================================
# HOME / STUDENT LOGIN
# ============================================================

@app.route("/")
def home():

    return render_template("student-login.html")


# ============================================================
# STUDENT LOGIN
# ============================================================

@app.route("/student-login", methods=["POST"])
def student_login():

    try:

        data = request.get_json(silent=True) or {}

        student_id = data.get("student_id")
        password = data.get("password")

        if not student_id or not password:

            return {
                "success": False,
                "message": "Student ID and Password are required"
            }

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT student_id, name, class_name, password
            FROM students
            WHERE student_id = ?
        """, (student_id,))

        student = cursor.fetchone()

        connection.close()

        if student and student["password"] == password:

            return {
                "success": True,
                "student_id": student["student_id"],
                "name": student["name"],
                "class_name": student["class_name"]
            }

        return {
            "success": False,
            "message": "Invalid Student ID or Password"
        }

    except Exception as error:

        print("STUDENT LOGIN ERROR:", error)

        return {
            "success": False,
            "message": "Server error occurred"
        }, 500


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student-dashboard")
def student_dashboard():

    return render_template("student-dashboard.html")


# ============================================================
# GENERATE QR
# ============================================================

@app.route("/generate-qr")
def generate_qr():

    return render_template("generate-qr.html")


# ============================================================
# SCAN QR
# ============================================================

@app.route("/scan-qr")
def scan_qr():

    return render_template("scan-qr.html")


# ============================================================
# MARK ATTENDANCE
# ============================================================

@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():

    try:

        data = request.get_json(silent=True) or {}

        student_id = data.get("student_id")

        if not student_id:

            return {
                "success": False,
                "message": "Student ID not found"
            }

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT student_id
            FROM students
            WHERE student_id = ?
            """,
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

    except Exception as error:

        print("ATTENDANCE ERROR:", error)

        return {
            "success": False,
            "message": "Unable to mark attendance"
        }, 500


# ============================================================
# MY ATTENDANCE
# ============================================================

@app.route("/my-attendance")
def my_attendance():

    return render_template("my-attendance.html")


# ============================================================
# ATTENDANCE API
# ============================================================

@app.route("/api/attendance/<student_id>")
def get_attendance(student_id):

    try:

        connection = get_connection()
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
                "subject": record["subject"],
                "date": record["date"],
                "time": record["time"],
                "status": record["status"]
            })

        return attendance

    except Exception as error:

        print("ATTENDANCE FETCH ERROR:", error)

        return {
            "success": False,
            "message": "Unable to fetch attendance"
        }, 500


# ============================================================
# TEACHER LOGIN PAGE
# ============================================================

@app.route("/teacher-login", methods=["GET"])
def teacher_login_page():

    return render_template("teacher-login.html")


# ============================================================
# TEACHER LOGIN
# ============================================================

@app.route("/teacher-login", methods=["POST"])
def teacher_login():

    try:

        data = request.get_json(silent=True) or {}

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

    except Exception as error:

        print("TEACHER LOGIN ERROR:", error)

        return {
            "success": False,
            "message": "Server error occurred"
        }, 500


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if not session.get("teacher_logged_in"):

        return redirect("/teacher-login")

    return render_template("Teacher-Dashboard.html")
 

# ============================================================
# TEACHER ATTENDANCE
# ============================================================

@app.route("/teacher-attendance")
def teacher_attendance():

    if not session.get("teacher_logged_in"):

        return redirect("/teacher-login")

    try:

        connection = get_connection()
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

    except Exception as error:

        print("TEACHER ATTENDANCE ERROR:", error)

        return "Unable to load attendance", 500


# ============================================================
# ATTENDANCE REPORT
# ============================================================

@app.route("/attendance-report")
def attendance_report():

    if not session.get("teacher_logged_in"):

        return redirect("/teacher-login")

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                student_id,
                SUM(
                    CASE
                        WHEN status = 'Present' THEN 1
                        ELSE 0
                    END
                ),
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
                (present / total) * 100,
                2
            ) if total > 0 else 0

            reports.append(
                (
                    student_id,
                    present,
                    total,
                    percentage
                )
            )

        return render_template(
            "attendance-report.html",
            reports=reports
        )

    except Exception as error:

        print("REPORT ERROR:", error)

        return "Unable to generate report", 500


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ============================================================
# TEACHER LOGOUT
# ============================================================

@app.route("/teacher-logout")
def teacher_logout():

    session.clear()

    return redirect("/teacher-login")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "message": "Smart Attendance server is running"
    }


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )

