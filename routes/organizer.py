from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from functools import wraps
from models.event import get_events_by_organizer, create_event, get_event_by_id, update_event_status
from models.registration import get_registrations_for_event, update_attendance

organizer_bp = Blueprint('organizer', __name__)

def organizer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'organizer':
            flash('Organizer access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@organizer_bp.route('/')
@login_required
@organizer_required
def dashboard():
    events = get_events_by_organizer(current_user.id)
    return render_template('organizer/dashboard.html', events=events)

@organizer_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
@organizer_required
def new_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        venue = request.form.get('venue')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        registration_deadline = request.form.get('registration_deadline')
        capacity = request.form.get('capacity')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        min_team_size = request.form.get('min_team_size', 1, type=int)
        max_team_size = request.form.get('max_team_size', 1, type=int)
        
        create_event(title, description, category, venue, event_date, event_time, registration_deadline, capacity, current_user.id, contact_email, contact_phone, min_team_size, max_team_size)
        flash('Event created successfully!', 'success')
        return redirect(url_for('organizer.dashboard'))
    return render_template('organizer/create_event.html')

@organizer_bp.route('/event/<int:event_id>/attendance', methods=['GET', 'POST'])
@login_required
@organizer_required
def attendance(event_id):
    event = get_event_by_id(event_id)
    if not event or event['organizer_id'] != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('organizer.dashboard'))
        
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('attendance_'):
                reg_id = key.split('_')[1]
                update_attendance(reg_id, value)
        update_event_status(event_id, 'completed')
        flash('Attendance updated successfully.', 'success')
        return redirect(url_for('organizer.dashboard'))

    registrations = get_registrations_for_event(event_id)
    return render_template('organizer/attendance.html', event=event, registrations=registrations)

@organizer_bp.route('/event/<int:event_id>')
@login_required
@organizer_required
def event_detail(event_id):
    event = get_event_by_id(event_id)
    if not event or event['organizer_id'] != current_user.id:
        return redirect(url_for('organizer.dashboard'))
    registrations = get_registrations_for_event(event_id)
    from models.feedback import get_feedback_for_event
    feedback = get_feedback_for_event(event_id)
    return render_template('organizer/event_detail.html', event=event, registrations=registrations, feedback=feedback)

@organizer_bp.route('/event/<int:event_id>/register_manual', methods=['POST'])
@login_required
@organizer_required
def register_manual(event_id):
    event = get_event_by_id(event_id)
    if not event or event['organizer_id'] != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for('organizer.dashboard'))
        
    participant_name = request.form.get('participant_name')
    participant_email = request.form.get('participant_email')
    team_name = request.form.get('team_name')
    team_members = request.form.get('team_members')
    
    from models.registration import create_registration, get_registration_by_email, count_event_registrations
    
    if get_registration_by_email(participant_email, event_id):
        flash("Email already registered for this event.", "error")
        return redirect(url_for('organizer.event_detail', event_id=event_id))
        
    current_count = count_event_registrations(event_id)
    status = 'registered'
    if current_count >= event['capacity']:
        status = 'waitlisted'
        flash("Capacity reached. Participant waitlisted.", "warning")
    else:
        flash("Registration successful.", "success")
        
    create_registration(participant_name, participant_email, team_name, team_members, event_id, status)
    
    return redirect(url_for('organizer.event_detail', event_id=event_id))

@organizer_bp.route('/api_stats')
@login_required
@organizer_required
def api_stats():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT r.attendance_status, COUNT(*) as count 
        FROM registrations r 
        JOIN events e ON r.event_id = e.id 
        WHERE e.organizer_id = ? 
        GROUP BY r.attendance_status
    """, (current_user.id,))
    reg_stats = cursor.fetchall()
    
    return {
        'attendance': {row['attendance_status']: row['count'] for row in reg_stats}
    }


@organizer_bp.route('/event/<int:event_id>/announce', methods=['POST'])
@login_required
@organizer_required
def announce(event_id):
    event = get_event_by_id(event_id)
    if not event or event['organizer_id'] != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for('organizer.dashboard'))
        
    message = request.form.get('message')
    if message:
        from models.registration import get_registrations_for_event
        registrations = get_registrations_for_event(event_id)
        # In production, send real emails to reg['participant_email'] via SMTP
        flash("Announcement sent to all registered and waitlisted participants.", "success")
        
    return redirect(url_for('organizer.event_detail', event_id=event_id))

@organizer_bp.route('/event/<int:event_id>/registration/<int:reg_id>/cancel', methods=['POST'])
@login_required
@organizer_required
def cancel_registration(event_id, reg_id):
    from models.registration import delete_registration, get_registration_by_id
    event = get_event_by_id(event_id)
    reg = get_registration_by_id(reg_id)
    
    if not event or event['organizer_id'] != current_user.id or not reg or reg['event_id'] != event_id:
        flash("Unauthorized action.", "error")
        return redirect(url_for('organizer.dashboard'))
        
    delete_registration(reg_id)
    flash("Registration cancelled and removed successfully.", "success")
    return redirect(url_for('organizer.event_detail', event_id=event_id))


@organizer_bp.route('/reports')
@login_required
@organizer_required
def reports():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT v.* 
        FROM event_analytics v 
        JOIN events e ON v.event_id = e.id 
        WHERE e.organizer_id = ?
    """, (current_user.id,))
    analytics = cursor.fetchall()
    return render_template('organizer/reports.html', analytics=analytics)

@organizer_bp.route('/reports/export')
@login_required
@organizer_required
def export_reports():
    from app import get_db
    import csv
    from io import StringIO
    
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT v.* 
        FROM event_analytics v 
        JOIN events e ON v.event_id = e.id 
        WHERE e.organizer_id = ?
    """, (current_user.id,))
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Event ID', 'Title', 'Category', 'Capacity', 'Total Registrations', 'Total Attended', 'Total Waitlisted', 'Average Rating'])
    
    for row in cursor.fetchall():
        cw.writerow([
            row['event_id'], row['title'], row['category'], row['capacity'],
            row['total_registrations'], row['total_attended'],
            row['total_waitlisted'], row['average_rating']
        ])
        
    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=my_event_analytics.csv"}
    )
