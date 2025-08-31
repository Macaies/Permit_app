# Permit_app
Land spaces permit
# Event Permit System

A modular, Flask-based web application for managing public event permit submissions, calendar availability, and admin oversight. Designed for civic transparency, stakeholder usability, and scalable workflows.

---

## 🌟 Features

- 🧾 **Multi-step Event Application Form**  
  7-step form with real-time validation, file uploads, and eligibility logic.

- 📍 **Location Feedback**  
  Smart keyword matching to validate civic spaces (parks, reserves, halls).

- 📅 **Calendar Availability Viewer**  
  Public-facing FullCalendar interface showing confirmed bookings.

- ✅ **Self-Assessable Checklist**  
  Auto-evaluates eligibility based on attendance, duration, and risk factors.

- 📤 **Messaging Module**  
  Sends confirmation emails to applicants upon submission.

- 🛠️ **Admin Dashboard**  
  Searchable list of applications with export and file access.

---

## 🧱 Tech Stack

- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, JavaScript (FullCalendar)  
- **Database:** SQLite  
- **Email:** SMTP (configurable)  
- **File Handling:** Secure uploads via `werkzeug`

---

## 🚀 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/ssc-event-permit.git
cd ssc-event-permit- Install dependencies
pip install -r requirements.txt


- Initialize the database
python app.py


- Run the app
python app.py


Visit http://127.0.0.1:5000/ to access the form.
Visit http://127.0.0.1:5000/calendar to view event availability.

📁 Project Structure
project/
├── app.py
├── config.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── calendar.html
│   ├── admin.html
│   ├── success.html
│   └── base.html
├── static/
│   ├── css/
│   ├── js/
├── modules/
│   ├── calendar.py
│   ├── location.py
│   ├── messaging.py
│   └── eligibility.py
├── uploads/
└── instance/
    └── sunshine.db



🛡️ Admin Access
To simulate admin access:
@app.route('/login-as-admin')
def login_as_admin():
    session["is_admin"] = True
    return redirect(url_for("admin"))



📬 Email Configuration
Update messaging.py with your SMTP credentials:
sender_email = "your-email@example.com"
sender_password = "your-app-password"



📦 Export & Backup
Use /export route to download all applications as CSV.

📜 License
MIT License — free to use, modify, and distribute.


