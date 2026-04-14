from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models.event import get_all_events, get_event_by_id
from models.registration import get_student_registrations, get_registration_by_email, count_event_registrations, create_registration
from models.feedback import create_feedback, has_submitted_feedback

student_bp = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Student access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/')
@login_required
@student_required
def dashboard():
    registrations = get_student_registrations(current_user.email)
    return render_template('student/dashboard.html', registrations=registrations)

@student_bp.route('/events')
@login_required
@student_required
def events_list():
    all_events = get_all_events()
    # Optional: filter only upcoming events
    upcoming_events = [e for e in all_events if e['status'] == 'upcoming']
    return render_template('student/events_list.html', events=upcoming_events)

@student_bp.route('/event/<int:event_id>')
@login_required
@student_required
def event_detail(event_id):
    event = get_event_by_id(event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('student.events_list'))
    
    existing_registration = get_registration_by_email(current_user.email, event_id)
    feedback_submitted = False
    if existing_registration:
        feedback_submitted = has_submitted_feedback(existing_registration['id'], event_id)
        
    return render_template('student/event_detail.html', event=event, existing_registration=existing_registration, feedback_submitted=feedback_submitted)

@student_bp.route('/event/<int:event_id>/feedback', methods=['POST'])
@login_required
@student_required
def submit_feedback(event_id):
    existing_registration = get_registration_by_email(current_user.email, event_id)
    if not existing_registration or existing_registration['attendance_status'] != 'attended':
        flash('You can only submit feedback for events you have attended.', 'error')
        return redirect(url_for('student.dashboard'))
        
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    try:
        rating = int(rating)
        create_feedback(existing_registration['id'], event_id, rating, comment)
        flash('Feedback submitted successfully. Thank you!', 'success')
    except Exception as e:
        flash('Error saving feedback.', 'error')
        
    return redirect(url_for('student.event_detail', event_id=event_id))

@student_bp.route('/event/<int:event_id>/register', methods=['POST'])
@login_required
@student_required
def register(event_id):
    event = get_event_by_id(event_id)
    if not event or event['status'] != 'upcoming':
        flash('Invalid event or event is no longer accepting registrations.', 'error')
        return redirect(url_for('student.events_list'))
        
    if get_registration_by_email(current_user.email, event_id):
        flash('You are already registered for this event.', 'error')
        return redirect(url_for('student.event_detail', event_id=event_id))
        
    team_name = request.form.get('team_name', '').strip()
    
    # We expect multiple inputs with name team_members[] from the dynamically generated form.
    # Exclude empty values.
    members_list = [m.strip() for m in request.form.getlist('team_members[]') if m.strip()]
    
    total_team_size = 1 + len(members_list)
    min_size = event.get('min_team_size', 1)
    max_size = event.get('max_team_size', 1)
    
    if max_size > 1 and total_team_size < min_size:
        flash(f'Minimum team size for this event is {min_size}. You only have {total_team_size}.', 'error')
        return redirect(url_for('student.event_detail', event_id=event_id))
    
    if total_team_size > max_size:
        flash(f'Maximum team size for this event is {max_size}. You have {total_team_size}.', 'error')
        return redirect(url_for('student.event_detail', event_id=event_id))
        
    team_members_str = ", ".join(members_list) if members_list else None
    
    current_count = count_event_registrations(event_id)
    status = 'registered'
    if current_count >= event['capacity']:
        status = 'waitlisted'
        flash("Capacity reached. You have been waitlisted.", "warning")
    else:
        flash("Registration successful.", "success")
        
    create_registration(
        participant_name=current_user.name,
        participant_email=current_user.email,
        team_name=team_name,
        team_members=team_members_str,
        event_id=event_id,
        status=status
    )
    
    return redirect(url_for('student.dashboard'))

@student_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
@student_required
def cancel_registration(event_id):
    from models.registration import delete_registration
    existing_registration = get_registration_by_email(current_user.email, event_id)
    if not existing_registration:
        flash("You are not registered for this event.", "error")
        return redirect(url_for('student.dashboard'))
        
    delete_registration(existing_registration['id'])
    flash("Your registration has been cancelled.", "success")
    return redirect(url_for('student.dashboard'))
