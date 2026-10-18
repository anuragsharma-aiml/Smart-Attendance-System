
from flask import Flask, request, render_template, redirect, session
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

# SUPABASE CONNECTION
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL or SUPABASE_KEY is missing. Check your .env file."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# HOME / STUDENT LOGIN
@app.route("/")
def home():
    return render_template("student-login.html")


# STUDENT LOGIN
@app.route("/student-login", methods=["POST"])
def student_login():
    try:
        data = request.get_json(silent=True) or request.form
        student_id = (data.get("student_id") or "").strip()
        password = data.get("password") or ""

        if not student_id or not password:
            return {
                "success": False,
                "message": "Student ID and Password are required"
            }, 400

        result = (
            supabase.table("students")
            .select("student_id, name, class_name, password")
            .eq("student_id", student_id)
            .limit(1)
            .execute()
        )

        student = result.data[0] if result.data else None

        if not student or str(student.get("password") or "") != str(password):
            return {
                "success": False,
                "message": "Invalid Student ID or Password"
            }, 401

        session.clear()
        session["student_id"] = student["student_id"]
        session["student_name"] = student.get("name", "")
        session["student_class"] = student.get("class_name", "")

        return {
            "success": True,
            "student_id": student["student_id"],
            "name": student.get("name", ""),
            "class_name": student.get("class_name", "")
        }

    except Exception:
        app.logger.exception("STUDENT LOGIN ERROR")
        return {
            "success": False,
            "message": "Student login failed. Check Supabase settings."
        }, 500


# STUDENT DASHBOARD
@app.route("/student-dashboard")
def student_dashboard():
    if not session.get("student_id"):
        return redirect("/")

    student_id = session.get("student_id")
    print("DASHBOARD STUDENT ID:", repr(student_id))

    try:
        response = (
            supabase.table("attendance")
            .select("*")
            .eq("student_id", student_id)
            .order("id", desc=True)
            .execute()
        )

        attendance_records = response.data or []
        print("DASHBOARD ATTENDANCE RECORDS:", attendance_records)

        return render_template(
            "student-dashboard.html",
            attendance_records=attendance_records
        )

    except Exception as e:
        app.logger.exception("STUDENT DASHBOARD ERROR")
        return render_template(
            "student-dashboard.html",
            attendance_records=[],
            error="Attendance load nahi ho pa rahi. Please refresh karein."
        )


# GENERATE QR PAGE
@app.route("/generate-qr")
def generate_qr():
    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")
    return render_template("generate-qr.html")


# SCAN QR PAGE
@app.route("/scan-qr")
def scan_qr():
    if not session.get("student_id"):
        return redirect("/")
    return render_template("scan-qr.html")


# MARK ATTENDANCE
@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():
    try:
        logged_in_student = session.get("student_id")

        if not logged_in_student:
            return {
                "success": False,
                "message": "Please log in as a student first."
            }, 401

        data = request.get_json(silent=True) or {}
        qr_student_id = (data.get("student_id") or "").strip()

        if qr_student_id and qr_student_id != logged_in_student:
            return {
                "success": False,
                "message": "QR Student ID does not match your login."
            }, 403

        student_id = logged_in_student
        subject = (data.get("subject") or "QR Attendance").strip()

        if not subject:
            subject = "QR Attendance"

        student_result = (
            supabase.table("students")
            .select("student_id")
            .eq("student_id", student_id)
            .limit(1)
            .execute()
        )

        if not student_result.data:
            return {
                "success": False,
                "message": "Student not found."
            }, 404

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        existing = (
            supabase.table("attendance")
            .select("id")
            .eq("student_id", student_id)
            .eq("subject", subject)
            .eq("date", today)
            .limit(1)
            .execute()
        )

        if existing.data:
            return {
                "success": False,
                "message": "Attendance is already marked for this subject today."
            }, 409

        attendance_data = {
            "student_id": student_id,
            "subject": subject,
            "date": today,
            "time": now.strftime("%H:%M:%S"),
            "status": "Present"
        }

        try:
            supabase.table("attendance").insert(
                attendance_data,
                returning="minimal"
            ).execute()

        except Exception as insert_error:
            error_text = str(insert_error)

            if (
                "23505" in error_text
                or "attendance_one_per_student_subject_date" in error_text
            ):
                return {
                    "success": False,
                    "message": "Attendance is already marked for this subject today."
                }, 409

            raise

        app.logger.info(
            "Attendance marked for student %s, subject %s, date %s",
            student_id, subject, today
        )

        return {
            "success": True,
            "message": "Attendance marked successfully."
        }, 200

    except Exception:
        app.logger.exception("ATTENDANCE ERROR")
        return {
            "success": False,
            "message": "Unable to mark attendance. Please try again."
        }, 500


# MY ATTENDANCE PAGE
@app.route("/my-attendance")
def my_attendance():
    if not session.get("student_id"):
        return redirect("/")

    student_id = session.get("student_id")

    try:
        response = (
            supabase.table("attendance")
            .select("*")
            .eq("student_id", student_id)
            .order("id", desc=True)
            .execute()
        )

        attendance_records = response.data or []
        print("LOGGED-IN STUDENT:", repr(student_id))
        print("ATTENDANCE RECORDS FROM SUPABASE:", attendance_records)

        return render_template(
            "my-attendance.html",
            student_id=student_id,
            attendance_records=attendance_records
        )

    except Exception:
        app.logger.exception("MY ATTENDANCE ERROR")
        return render_template(
            "my-attendance.html",
            student_id=student_id,
            attendance_records=[],
            error="Attendance load nahi ho pa rahi. Please try again."
        )


# STUDENT ATTENDANCE API
@app.route("/api/attendance/<student_id>")
def get_attendance(student_id):
    try:
        # Students can view only their own attendance
        if session.get("student_id") != student_id:
            return {"success": False, "message": "Unauthorized"}, 403

        result = (
            supabase.table("attendance")
            .select("subject, date, time, status")
            .eq("student_id", student_id)
            .order("date", desc=True)
            .order("time", desc=True)
            .execute()
        )

        return result.data

    except Exception:
        app.logger.exception("ATTENDANCE FETCH ERROR")
        return {
            "success": False,
            "message": "Unable to fetch attendance."
        }, 500


# TEACHER LOGIN PAGE
@app.route("/teacher-login", methods=["GET"])
def teacher_login_page():
    return render_template("teacher-login.html")


# TEACHER LOGIN API
@app.route("/teacher-login", methods=["POST"])
def teacher_login():
    try:
        data = request.get_json(silent=True) or request.form
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        teacher_email = os.environ.get("TEACHER_EMAIL", "teacher@gmail.com")
        teacher_password = os.environ.get("TEACHER_PASSWORD", "12345")

        if email == teacher_email and password == teacher_password:
            session.clear()
            session["teacher_logged_in"] = True
            return {
                "success": True,
                "message": "Teacher login successful"
            }

        return {
            "success": False,
            "message": "Invalid Teacher Email or Password"
        }, 401

    except Exception:
        app.logger.exception("TEACHER LOGIN ERROR")
        return {
            "success": False,
            "message": "Teacher login failed."
        }, 500


# TEACHER DASHBOARD
@app.route("/teacher-dashboard")
def teacher_dashboard():
    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")
    return render_template("Teacher-Dashboard.html")


# TEACHER ATTENDANCE TABLE

# TEACHER ATTENDANCE TABLE
@app.route("/teacher-attendance")
def teacher_attendance():
    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")

    try:
        result = (
            supabase.table("attendance")
            .select("student_id, subject, date, time, status")
            .order("date", desc=True)
            .order("time", desc=True)
            .execute()
        )

        app.logger.info(
            "Teacher attendance rows fetched: %s",
            len(result.data or [])
        )

        return render_template(
            "teacher-attendance.html",
            records=result.data or []
        )

    except Exception as e:
        app.logger.exception("TEACHER ATTENDANCE ERROR")
        return f"Teacher attendance error: {str(e)}", 500

# ATTENDANCE REPORT
@app.route("/attendance-report")
def attendance_report():
    if not session.get("teacher_logged_in"):
        return redirect("/teacher-login")

    try:
        result = (
            supabase.table("attendance")
            .select("student_id, status")
            .execute()
        )

        student_data = {}

        for record in result.data:
            student_id = record["student_id"]
            status = record["status"]

            if student_id not in student_data:
                student_data[student_id] = {"present": 0, "total": 0}

            student_data[student_id]["total"] += 1

            if status == "Present":
                student_data[student_id]["present"] += 1

        reports = []

        for student_id, data in student_data.items():
            present = data["present"]
            total = data["total"]
            percentage = round((present / total) * 100, 2) if total else 0

            reports.append((student_id, present, total, percentage))

        return render_template(
            "attendance-report.html",
            reports=reports
        )

    except Exception as e:
         app.logger.exception("TEACHER ATTENDANCE ERROR")
         return f"Unable to load attendance: {str(e)}", 500


# STUDENT LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# TEACHER LOGOUT
@app.route("/teacher-logout")
def teacher_logout():
    session.clear()
    return redirect("/teacher-login")


# HEALTH CHECK
@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "Smart Attendance server is running"
    }


# START SERVER
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

