from datetime import datetime

def reserve(event_date_str, start_time_str):
    """
    Checks if the event date is valid and not on a weekend.
    Returns a status message.
    """
    try:
        # Combine date and time into a datetime object
        dt_str = f"{event_date_str} {start_time_str}"
        event_datetime = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

        # Check if it's a weekend
        if event_datetime.weekday() >= 5:
            return "⚠️ Event is scheduled on a weekend. Additional review may be required."

        # Placeholder for future conflict check
        # e.g. check DB for overlapping events

        return "✅ Date and time are available."
    except Exception as e:
        return f"❌ Invalid date/time format: {e}"