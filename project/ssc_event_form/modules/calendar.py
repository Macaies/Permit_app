from datetime import datetime
from db import get_db

def reserve(event_date_str, start_time_str):
    try:
        dt_str = f"{event_date_str} {start_time_str}"
        event_datetime = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        if event_datetime.weekday() >= 5:
            return "⚠️ Event is scheduled on a weekend. Additional review may be required."
        return "✅ Date and time are available."
    except Exception as e:
        return f"❌ Invalid date/time format: {e}"

def get_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT event_name, event_date FROM applications")
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "title": row["event_name"],
            "start": row["event_date"]
        })
    return events