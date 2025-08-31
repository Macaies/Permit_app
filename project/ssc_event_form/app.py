from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response, session, abort, jsonify
import os
import csv
from werkzeug.utils import secure_filename
from config import SECRET_KEY, UPLOAD_FOLDER, DATABASE
from db import get_db, init_db

# Modular civic logic
from modules import location, calendar, messaging, eligibility

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = DATABASE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-as-admin')
def login_as_admin():
    session["is_admin"] = True
    flash("Logged in as admin.", "info")
    return redirect(url_for("admin"))

@app.route('/submit', methods=['POST'])
def submit():
    files = request.files
    form = request.form.to_dict()

    # File uploads
    insurance_file = None
    site_map_file = None
    if 'insurance' in files and files['insurance'].filename:
        insurance_file = secure_filename(files['insurance'].filename)
        files['insurance'].save(os.path.join(app.config['UPLOAD_FOLDER'], insurance_file))
    if 'site_map' in files and files['site_map'].filename:
        site_map_file = secure_filename(files['site_map'].filename)
        files['site_map'].save(os.path.join(app.config['UPLOAD_FOLDER'], site_map_file))

    form['insurance_file'] = insurance_file
    form['site_map'] = site_map_file

    # Civic logic
    form['self_assessable'] = eligibility.check(
        form.get("attendance", 0),
        form.get("alcohol", "No"),
        form.get("duration", "More")
    )
    form['location_valid'] = location.validate(form.get("event_location", ""))
    form['calendar_status'] = calendar.reserve(form.get("event_date"), form.get("start_time"))

    # Save to DB
    conn = get_db()
    cursor = conn.cursor()
    columns = ", ".join(form.keys())
    placeholders = ", ".join(["?"] * len(form))
    cursor.execute(f"INSERT INTO applications ({columns}) VALUES ({placeholders})", tuple(form.values()))
    conn.commit()
    conn.close()

    # Messaging
    messaging.send(form['email'], form['event_name'])

    flash("Application submitted successfully!", "success")
    return redirect(url_for("success"))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin')
def admin():
    if not session.get("is_admin"):
        abort(403)
    q = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    if q:
        cursor.execute("""
            SELECT * FROM applications
            WHERE applicant_name LIKE ? OR event_name LIKE ?
            ORDER BY id DESC
        """, (f'%{q}%', f'%{q}%'))
    else:
        cursor.execute("SELECT * FROM applications ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin.html', rows=rows)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/export')
def export():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    conn.close()

    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(rows[0].keys() if rows else [])
    for row in rows:
        cw.writerow([row[k] for k in row.keys()])
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=applications.csv"})

@app.route('/events')
def events():
    if not session.get("is_admin"):
        abort(403)
    return jsonify(calendar.get_events())

##@app.route('/calendar')
##def calendar_view():
##    if not session.get("is_admin"):
##        abort(403)
##    return render_template('calendar.html')
@app.route('/calendar')
def calendar_view():
    return render_template('calendar.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)