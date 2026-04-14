def create_feedback(registration_id, event_id, rating, comment):
    from app import get_db
    db = get_db()
    db.execute(
        "INSERT INTO feedback (registration_id, event_id, rating, comment) VALUES (?, ?, ?, ?)",
        (registration_id, event_id, rating, comment)
    )
    db.commit()

def get_feedback_for_event(event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT f.*, r.participant_name as participant_name FROM feedback f JOIN registrations r ON f.registration_id = r.id WHERE f.event_id = ? ORDER BY f.submitted_at DESC", 
        (event_id,)
    )
    return [dict(r) for r in cursor.fetchall()]

def has_submitted_feedback(registration_id, event_id):
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT id FROM feedback WHERE registration_id = ? AND event_id = ?", (registration_id, event_id))
    return cursor.fetchone() is not None
