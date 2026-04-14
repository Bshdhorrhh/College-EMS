from flask import Blueprint, render_template, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from functools import wraps
from models.event import get_all_events, count_events
from models.user import get_all_users

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    events_count = count_events()
    users = get_all_users()
    return render_template('admin/dashboard.html', events_count=events_count, total_users=len(users))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users_list = get_all_users()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/api_stats')
@login_required
@admin_required
def api_stats():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM events GROUP BY category")
    categories = cursor.fetchall()
    
    cursor.execute("SELECT attendance_status, COUNT(*) as count FROM registrations GROUP BY attendance_status")
    reg_stats = cursor.fetchall()

    return {
        'categories': {row['category']: row['count'] for row in categories},
        'attendance': {row['attendance_status']: row['count'] for row in reg_stats}
    }

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM event_analytics")
    analytics = cursor.fetchall()
    return render_template('admin/reports.html', analytics=analytics)

@admin_bp.route('/reports/export')
@login_required
@admin_required
def export_reports():
    from app import get_db
    import csv
    from io import StringIO
    
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM event_analytics")
    
    si = StringIO()
    cw = csv.writer(si)
    
    cw.writerow(['Event ID', 'Title', 'Category', 'Capacity', 'Organizer Name', 'Total Registrations', 'Total Attended', 'Total Waitlisted', 'Average Rating'])
    
    for row in cursor.fetchall():
        cw.writerow([
            row['event_id'], row['title'], row['category'], row['capacity'],
            row['organizer_name'], row['total_registrations'], row['total_attended'],
            row['total_waitlisted'], row['average_rating']
        ])
        
    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=event_analytics.csv"}
    )

@admin_bp.route('/audit_logs')
@login_required
@admin_required
def audit_logs():
    from app import get_db
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    return render_template('admin/audit_logs.html', logs=logs)
