import sqlite3
import os

DATABASE = os.path.join('instance', 'sunshine.db')

def get_db():
    """Connect to SQLite DB (stored in instance/sunshine.db)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn

def init_db():
    """Initialize DB with full applications table for all steps."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            abn TEXT,
            contact_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            insurance_file TEXT,
            event_name TEXT NOT NULL,
            location TEXT NOT NULL,
            event_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            finish_time TEXT,
            attendance INTEGER,
            setup_datetime TEXT,
            cleanup_datetime TEXT,
            fundraising TEXT,
            fundraising_purpose TEXT,
            next_year_date TEXT,
            wet_weather TEXT,
            event_description TEXT,
            food_served TEXT,
            food_details TEXT,
            alcohol TEXT,
            liquor_holder TEXT,
            dispensing_areas INTEGER,
            consumption_boundaries TEXT,
            electricity_access TEXT,
            electricity_details TEXT,
            generators TEXT,
            generator_details TEXT,
            toilets TEXT,
            toilets_male INTEGER,
            toilets_female INTEGER,
            toilets_disabled INTEGER,
            bins_provided TEXT,
            waste_plan TEXT,
            structures TEXT,
            structures_details TEXT,
            amusement_devices TEXT,
            amusement_details TEXT,
            animals TEXT,
            animal_details TEXT,
            parking TEXT,
            parking_details TEXT,
            first_aid TEXT,
            first_aid_details TEXT,
            emergency_notified TEXT,
            emergency_details TEXT,
            security TEXT,
            security_details TEXT,
            noise TEXT,
            noise_plan TEXT,
            lighting TEXT,
            lighting_details TEXT,
            site_map TEXT,
            community_consultation TEXT,
            consultation_details TEXT,
            cultural_considerations TEXT,
            cultural_details TEXT,
            accessibility_plan TEXT,
            sustainability TEXT,
            sustainability_details TEXT,
            notification_plan TEXT,
            volunteers TEXT,
            volunteer_details TEXT,
            digital_signature TEXT,
            declaration_date TEXT
        )
    ''')
    conn.commit()
    conn.close()