 # Smart Attendance Management System

A QR Code-Based Attendance Management System built with **Python, Flask, Supabase, HTML, CSS, and JavaScript**.

The application enables students to mark attendance by scanning QR codes and allows teachers to manage and review attendance records through a web-based interface.

## Features

- **Student Authentication** — Student login and dashboard.
- **Teacher Authentication** — Separate teacher login and dashboard.
- **QR Code Generation** — Generate QR codes associated with a subject.
- **QR Code Attendance** — Scan a QR code to submit attendance.
- **Cloud Database** — Store student and attendance records in Supabase.
- **Attendance History** — View attendance records from the application.
- **Attendance Reports** — Access attendance information for review.
- **Duplicate Prevention** — Prevent duplicate attendance entries for the same student, subject, and date.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web framework |
| Supabase | Cloud database |
| HTML | Page structure |
| CSS | User interface styling |
| JavaScript | Client-side interactions |
| QR Code | Attendance scanning workflow |

## How It Works

1. A student or teacher logs in through the appropriate interface.
2. The teacher generates a QR code for a subject.
3. The student scans the QR code.
4. The application processes the attendance request.
5. Attendance data is stored in Supabase.
6. Teachers can review attendance records and reports.

## Project Structure

```text
Smart-Attendance-System/
├── app.py
├── requirements.txt
├── vercel.json
├── README.md
├── .gitignore
├── templates/
├── static/
└── index.html
```

*The structure above represents the repository layout; individual template and static files may vary.*

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- A Supabase project
- Git

### 1. Clone the repository

```bash
git clone https://github.com/anuragsharma-aiml/Smart-Attendance-System.git
cd Smart-Attendance-System
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_publishable_key
```

Replace the example values with your own Supabase project credentials. Never commit your `.env` file or expose secret keys publicly.

### 5. Run the application

```powershell
python app.py
```

Open the local URL printed by Flask in your browser.

## Database

The application uses Supabase to store student information and attendance records. Configure the required tables and access policies in your Supabase project before running the application.

## Security Notes

- Keep credentials in environment variables.
- Do not commit `.env` files or private keys.
- Configure appropriate Supabase Row Level Security (RLS) policies and authentication checks before public deployment.

## Future Improvements

- Improved attendance analytics and downloadable reports
- Stronger role-based access controls
- Enhanced deployment and production security
- Improved mobile responsiveness

## Author

**Anurag Sharma**
B.Tech CSE (AI & ML) Student

---

*Built as a practical project to explore web development, QR code workflows, and cloud database integration.*
