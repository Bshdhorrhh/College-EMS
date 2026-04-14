def get_all_events():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
    return [dict(r) for r in cursor.fetchall()]

def get_events_by_organizer(organizer_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM events WHERE organizer_id = ? ORDER BY event_date DESC", (organizer_id,))
    return [dict(r) for r in cursor.fetchall()]

def get_event_by_id(event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_event(title, description, category, venue, event_date, event_time, registration_deadline, capacity, organizer_id, contact_email, contact_phone, min_team_size, max_team_size):
    from app import get_db
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO events (title, description, category, venue, event_date, event_time, registration_deadline, capacity, organizer_id, contact_email, contact_phone, min_team_size, max_team_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (title, description, category, venue, event_date, event_time, registration_deadline, capacity, organizer_id, contact_email, contact_phone, min_team_size, max_team_size)
    )
    db.commit()
    return cursor.lastrowid

def update_event_status(event_id, status):
    from app import get_db
    db = get_db()
    db.execute("UPDATE events SET status = ? WHERE id = ?", (status, event_id))
    db.commit()

def count_events():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) as c FROM events")
    return cursor.fetchone()['c']
