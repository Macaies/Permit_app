from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response, send_from_directory
from datetime import datetime
import os, io, csv, xlsxwriter
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER, SECRET_KEY
from db import get_conn
from modules import calendar

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- Helpers ----------------
def _save(file_field: str):
    """Save an uploaded file (if provided) into UPLOAD_FOLDER; return stored filename or None."""
    f = request.files.get(file_field)
    if not f or not f.filename:
        return None
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    name = secure_filename(f.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], name)
    f.save(path)
    return name

# ---------- Classification Rules ----------
def classify_event(form):
    attendance = int(form.get("attendance", 0) or 0)
    alcohol = form.get("alcohol", "No")
    high_risk = form.get("high_risk", "No")
    traffic = form.get("traffic_mgmt", "No")
    vehicle_access = form.get("vehicle_access", "No")
    amplified = form.get("amplified_sound", "No")
    noise_level = int(form.get("noise_level", 0) or 0)
    total_days = int(form.get("total_days", 0) or 0)

    classification = "Self-assessable"
    if attendance >= 200: classification = "Assessable"
    if alcohol == "Yes": classification = "Assessable"
    if high_risk == "Yes": classification = "Assessable"
    if traffic == "Yes": classification = "Assessable"
    if vehicle_access == "Yes": classification = "Assessable"
    if amplified == "Yes" and noise_level > 95: classification = "Assessable"
    if total_days > 2: classification = "Assessable"
    return classification

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    form = request.form.to_dict()

    # Map frontend -> DB fields
    form["applicant_name"]  = form.get("organizer_name", "")
    form["applicant_email"] = form.get("contact_email", "")
    form["applicant_phone"] = form.get("contact_phone", "")
    form["location"]        = form.get("venue", "")

    # Uploaded files
    insurance_file = _save("insurance_doc")
    site_map       = _save("site_map")
    other_files    = _save("other_docs")

    classification = classify_event(form)
    status = "Approved" if classification == "Self-assessable" else "Pending"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build columns & values from a single source of truth (prevents mismatch)
    cols = [
        "event_type", "applicant_name", "applicant_email", "applicant_phone",
        "event_name", "location", "start_date", "end_date", "start_time", "end_time",
        "attendance", "alcohol", "high_risk", "traffic_mgmt", "vehicle_access",
        "amplified_sound", "noise_level", "total_days", "notes",
        "insurance_file", "site_map", "other_files",
        # --- GIS fields (populated by map) ---
        "latitude", "longitude", "arcgis_feature_id", "arcgis_feature_name", "arcgis_layer",
        # -------------------------------------
        "classification", "status", "created_at"
        # id is autoincrement → do not include
    ]
    vals = (
        form.get("event_type"),
        form.get("applicant_name"),
        form.get("applicant_email"),
        form.get("applicant_phone"),
        form.get("event_name"),
        form.get("location"),
        form.get("start_date"),
        form.get("end_date") or form.get("start_date"),
        form.get("start_time"),
        form.get("end_time"),
        int(form.get("attendance", 0) or 0),
        form.get("alcohol", "No"),
        form.get("high_risk", "No"),
        form.get("traffic_mgmt", "No"),
        form.get("vehicle_access", "No"),
        form.get("amplified_sound", "No"),
        int(form.get("noise_level", 0) or 0),
        int(form.get("total_days", 1) or 1),
        form.get("notes"),
        insurance_file, site_map, other_files,
        request.form.get("latitude") or None,
        request.form.get("longitude") or None,
        request.form.get("arcgis_feature_id") or None,
        request.form.get("arcgis_feature_name") or None,
        request.form.get("arcgis_layer") or None,
        classification, status, now
    )
    assert len(cols) == len(vals), f"Columns ({len(cols)}) != Values ({len(vals)})"
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO events ({','.join(cols)}) VALUES ({placeholders})"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()

    # If self-assessable, reserve on internal calendar (after DB commit)
    if classification == "Self-assessable":
        try:
            calendar.reserve(
                title=form.get("event_name"),
                date_str=form.get("start_date"),
                start_time=form.get("start_time"),
                finish_time=form.get("end_time"),
                auto=True
            )
        except Exception as e:
            print("Calendar reserve failed:", e)

    return redirect(url_for(
        "success",
        classification=classification,
        applicant_name=form.get("applicant_name", ""),
        event_name=form.get("event_name", "")
    ))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)

@app.route("/success")
def success():
    return render_template("success.html",
        classification=request.args.get("classification","Self-assessable")
    )

@app.route("/admin")
def admin():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    query = "SELECT * FROM events WHERE 1=1"
    params = []
    if q:
        query += " AND (applicant_name LIKE ? OR event_type LIKE ? OR event_name LIKE ?)"
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if status:
        if status in ("Self-assessable", "Assessable"):
            query += " AND classification = ?"
            params.append(status)
        elif status in ("Pending", "Approved", "Rejected", "Cancelled"):
            query += " AND status = ?"
            params.append(status)
    query += " ORDER BY created_at DESC"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        applications = cur.fetchall()

    return render_template("admin.html", applications=applications)

@app.route("/export/<format>")
def export_data(format):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM events ORDER BY created_at DESC")
        rows = cur.fetchall()

    if format == "csv":
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(list(rows[0].keys()) if rows else [])
        for r in rows:
            cw.writerow([r[k] for k in r.keys()])
        return Response(si.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition":"attachment;filename=events.csv"})

    if format == "xlsx":
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {"in_memory": True})
        ws = wb.add_worksheet("Events")
        if rows:
            for c, key in enumerate(rows[0].keys()):
                ws.write(0, c, key)
        for r_i, r in enumerate(rows, start=1):
            for c, key in enumerate(r.keys()):
                ws.write(r_i, c, r[key])
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True,
                         download_name="events.xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return "Unsupported format", 400

@app.route("/api/events")
def api_events():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, event_name, start_date, end_date, start_time, end_time,
                   classification, status, location
            FROM events
            ORDER BY start_date ASC, start_time ASC
        """)
        rows = cur.fetchall()

    def to_iso(d, t):
        if not d: return None
        return f"{d}T{(t or '00:00')}:00"

    status_class = {
        "Approved": "fc-approved",
        "Pending":  "fc-pending",
        "Rejected": "fc-rejected",
        "Cancelled":"fc-rejected",
    }

    events = [{
        "id": r["id"],
        "title": r["event_name"],
        "start": to_iso(r["start_date"], r["start_time"]),
        "end":   to_iso(r["end_date"],   r["end_time"]),
        "extendedProps": {
            "classification": r["classification"],
            "status": r["status"],
            "location": r["location"]
        },
        "className": status_class.get(r["status"], "fc-pending")
    } for r in rows]

    return jsonify(events)

@app.route("/calendar")
def calendar_view():
    return render_template("calendar.html")

@app.route("/admin/event/<int:event_id>/<action>")
def update_event_status(event_id, action):
    new_status = None
    if action == "approve": new_status = "Approved"
    if action == "reject": new_status = "Rejected"
    if not new_status:
        return "Invalid action", 400

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE events SET status=? WHERE id=?", (new_status, event_id))
        conn.commit()
    return redirect(url_for("admin"))

@app.route("/api/event/<int:event_id>/status", methods=["POST"])
def api_update_status(event_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("Approved", "Pending", "Rejected", "Cancelled"):
        return jsonify({"ok": False, "error": "Invalid status"}), 400
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE events SET status=? WHERE id=?", (new_status, event_id))
        conn.commit()
    return jsonify({"ok": True})

@app.route("/admin/quick_book", methods=["POST"])
def admin_quick_book():
    data = request.get_json(force=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cols = [
        "event_type", "applicant_name", "applicant_email", "applicant_phone",
        "event_name", "location", "start_date", "end_date", "start_time", "end_time",
        "attendance", "alcohol", "high_risk", "traffic_mgmt", "vehicle_access",
        "amplified_sound", "noise_level", "total_days", "notes",
        "insurance_file", "site_map", "other_files",
        "latitude", "longitude", "arcgis_feature_id", "arcgis_feature_name", "arcgis_layer",
        "classification", "status", "created_at"
    ]
    vals = (
        "AdminBooking", "", "", "",
        data.get("event_name","Untitled"),
        data.get("location",""),
        data.get("start_date"), data.get("end_date"),
        data.get("start_time"), data.get("end_time"),
        0, "No", "No", "No", "No",
        "No", 0, 1, "",
        None, None, None,
        None, None, None, None, None,
        "Self-assessable", "Approved", now
    )
    assert len(cols) == len(vals)
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO events ({','.join(cols)}) VALUES ({placeholders})"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    # Ensure migration files exist (run scripts/migrate.py yourself as needed)
    if not os.path.exists("migrations/001_init.sql"):
        raise SystemExit("Missing migrations/001_init.sql. Create it first.")
    app.run(debug=True)
