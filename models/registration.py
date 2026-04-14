def get_registration_by_id(reg_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM registrations WHERE id = ?", (reg_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_registration_by_email(email, event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM registrations WHERE participant_email = ? AND event_id = ?", (email, event_id))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_registration(participant_name, participant_email, team_name, team_members, event_id, status='registered'):
    from app import get_db
    db = get_db()
    db.execute("""
        INSERT INTO registrations (participant_name, participant_email, team_name, team_members, event_id, attendance_status) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (participant_name, participant_email, team_name, team_members, event_id, status))
    db.commit()

def delete_registration(reg_id):
    from app import get_db
    db = get_db()
    
    # Needs to see if the user was taking a slot before deleting
    cursor = db.cursor()
    cursor.execute("SELECT * FROM registrations WHERE id = ?", (reg_id,))
    reg = cursor.fetchone()
    if not reg:
        return
        
    db.execute("DELETE FROM registrations WHERE id = ?", (reg_id,))
    db.commit()
    
    # Auto-promote oldest waitlisted participant if a registered slot just opened
    if reg['attendance_status'] in ['registered', 'attended']:
        event_id = reg['event_id']
        oldest_waitlist = get_oldest_waitlisted(event_id)
        if oldest_waitlist:
            update_attendance(oldest_waitlist['id'], 'registered')

def get_oldest_waitlisted(event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM registrations WHERE event_id = ? AND attendance_status = 'waitlisted' ORDER BY registered_at ASC LIMIT 1", (event_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_registrations_for_event(event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM registrations WHERE event_id = ?", (event_id,))
    return [dict(r) for r in cursor.fetchall()]

def get_student_registrations(email):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT r.*, e.title as event_title, e.event_date, e.event_time, e.venue 
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.participant_email = ?
        ORDER BY e.event_date DESC
    """, (email,))
    return [dict(r) for r in cursor.fetchall()]
        

def count_event_registrations(event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) as c FROM registrations WHERE event_id = ? AND attendance_status != 'waitlisted'", (event_id,))
    return cursor.fetchone()['c']

def update_attendance(registration_id, status):
    from app import get_db
    db = get_db()
    db.execute("UPDATE registrations SET attendance_status = ? WHERE id = ?", (status, registration_id))
    db.commit()
