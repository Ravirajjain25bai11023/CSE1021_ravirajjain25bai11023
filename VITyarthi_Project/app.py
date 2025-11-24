import os
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file

# Imports
from modules.auth import AuthManager
from modules.goals import GoalManager
from modules.subjects import SubjectManager
from modules.reports import ReportGenerator
from modules.charts import ChartGenerator
from modules.exports import DataExporter

app = Flask(__name__)

# Config
app.secret_key = 'your_secret_key_change_in_production_2024'
CHARTS_DIR = os.path.join('static', 'charts')
app.config['UPLOAD_FOLDER'] = CHARTS_DIR

# DB Connection
db_conf = {
    'host': 'localhost',
    'user': 'root',
    'password': '@RaviraajJain5',
    'database': 'student_tracker_db'
}

# Helpers
auth = AuthManager(db_conf)
goals = GoalManager(db_conf)
subjects = SubjectManager(db_conf)
reports = ReportGenerator(db_conf)
charts = ChartGenerator(db_conf, CHARTS_DIR)
exporter = DataExporter(db_conf)

# Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Auth ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    user = request.form.get('username')
    email = request.form.get('email')
    pwd = request.form.get('password')
    
    if pwd != request.form.get('confirm_password'):
        flash('Passwords do not match', 'error')
        return redirect(url_for('register'))
    
    resp = auth.register_user(user, email, pwd)
    
    if not resp['success']:
        flash(resp['message'], 'error')
        return redirect(url_for('register'))

    flash('Registered! Please login.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    resp = auth.login_user(request.form.get('email'), request.form.get('password'))
    
    if not resp['success']:
        flash(resp['message'], 'error')
        return redirect(url_for('login'))

    session['user_id'] = resp['user_id']
    session['username'] = resp['username']
    auth.update_streak(resp['user_id'])
    
    flash('Welcome back!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

# --- Core Views ---

@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    
    # Refresh charts
    charts.generate_goal_completion_chart(uid)
    charts.generate_weekly_progress_chart(uid)
    charts.generate_subject_performance_chart(uid)
    
    return render_template('dashboard.html', 
        stats=goals.get_user_stats(uid),
        activities=auth.get_recent_activities(uid, limit=10),
        deadlines=goals.get_upcoming_deadlines(uid, days=7),
        streak=auth.get_streak_info(uid)
    )

# Note: endpoint='goals' maps the function 'goals_view' to url_for('goals')
@app.route('/goals', endpoint='goals')
@login_required
def goals_view():
    uid = session['user_id']
    return render_template('goals.html', 
        goals=goals.get_user_goals(uid), 
        subjects=subjects.get_user_subjects(uid)
    )

@app.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    uid = session['user_id']
    f = request.form
    
    resp = goals.create_goal(
        uid, 
        f.get('subject'), 
        f.get('target_score'), 
        f.get('deadline'), 
        f.get('description', '')
    )
    
    if resp['success']:
        auth.log_activity(uid, 'goal_created', f"Goal: {f.get('subject')}")
        flash('Goal created!', 'success')
    else:
        flash(resp['message'], 'error')
    
    return redirect(url_for('goals'))

@app.route('/goals/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    uid = session['user_id']
    prog = request.form.get('progress')
    
    resp = goals.update_goal_progress(goal_id, uid, prog)
    
    if resp['success']:
        auth.log_activity(uid, 'goal_updated', f'Progress: {prog}%')
        if int(prog) == 100:
            auth.award_badge(uid, 'Goal Master', 'achievement')
            flash('Goal completed! 🎉', 'success')
    else:
        flash(resp['message'], 'error')
        
    return redirect(url_for('goals'))

@app.route('/goals/delete/<int:goal_id>')
@login_required
def delete_goal(goal_id):
    uid = session['user_id']
    resp = goals.delete_goal(goal_id, uid)
    
    if resp['success']:
        auth.log_activity(uid, 'goal_deleted', 'Deleted goal')
        flash('Goal deleted', 'info')
    
    return redirect(url_for('goals'))

@app.route('/subjects', endpoint='subjects')
@login_required
def subjects_view():
    return render_template('subjects.html', 
        subjects=subjects.get_user_subjects_with_progress(session['user_id'])
    )

@app.route('/subjects/add', methods=['POST'])
@login_required
def add_subject():
    uid = session['user_id']
    name = request.form.get('subject_name')
    
    resp = subjects.create_subject(uid, name)
    
    if resp['success']:
        auth.log_activity(uid, 'subject_added', f'Subject: {name}')
        flash('Subject added!', 'success')
    else:
        flash(resp['message'], 'error')
    
    return redirect(url_for('subjects'))

@app.route('/subjects/<int:subject_id>/log', methods=['POST'])
@login_required
def log_progress(subject_id):
    uid = session['user_id']
    resp = subjects.log_subject_progress(
        subject_id, 
        uid, 
        request.form.get('marks_scored'), 
        request.form.get('notes', '')
    )
    
    if resp['success']:
        auth.log_activity(uid, 'progress_logged', 'Logged progress')
        flash('Progress logged!', 'success')
    else:
        flash(resp['message'], 'error')
    
    return redirect(url_for('subjects'))

@app.route('/reports', endpoint='reports')
@login_required
def reports_view():
    uid = session['user_id']
    return render_template('reports.html', 
        weekly=reports.generate_weekly_report(uid),
        monthly=reports.generate_monthly_report(uid),
        subjects=reports.generate_subject_summary(uid)
    )

@app.route('/badges', endpoint='badges')
@login_required
def badges_view():
    uid = session['user_id']
    return render_template('badges.html', 
        earned=auth.get_user_badges(uid),
        available=auth.get_available_badges()
    )

@app.route('/profile')
@login_required
def profile():
    uid = session['user_id']
    return render_template('profile.html', 
        user=auth.get_user_info(uid), 
        stats=goals.get_user_stats(uid)
    )

# --- EXPORTS (Split up to fix template errors) ---

@app.route('/export/goals')
@login_required
def export_goals():
    uid = session['user_id']
    f = exporter.export_goals_csv(uid)
    if f:
        return send_file(f, as_attachment=True, download_name='my_goals.csv')
    flash('Export failed', 'error')
    return redirect(url_for('goals'))

@app.route('/export/progress')
@login_required
def export_progress():
    uid = session['user_id']
    f = exporter.export_progress_csv(uid)
    if f:
        return send_file(f, as_attachment=True, download_name='my_progress.csv')
    flash('Export failed', 'error')
    return redirect(url_for('subjects'))

@app.route('/export/reports')
@login_required
def export_reports():
    uid = session['user_id']
    f = exporter.export_reports_csv(uid)
    if f:
        return send_file(f, as_attachment=True, download_name='my_reports.csv')
    flash('Export failed', 'error')
    return redirect(url_for('reports'))

@app.route('/export/all')
@login_required
def export_all():
    uid = session['user_id']
    f = exporter.export_all_data(uid)
    if f:
        return send_file(f, as_attachment=True, download_name='student_data.zip')
    flash('Export failed', 'error')
    return redirect(url_for('profile'))

# --- Tools ---

@app.route('/study-timer')
@login_required
def study_timer():
    return render_template('study_timer.html')

@app.route('/study-timer/log', methods=['POST'])
@login_required
def log_study_session():
    uid = session['user_id']
    duration = request.form.get('duration')
    
    # Basic validation
    if not duration: return redirect(url_for('study_timer'))

    resp = subjects.log_study_session(uid, request.form.get('subject_id'), duration)
    
    if resp['success']:
        auth.log_activity(uid, 'study_session', f'Studied {duration}m')
        flash('Session logged!', 'success')
    
    return redirect(url_for('study_timer'))

@app.route('/todo', methods=['GET'])
@login_required
def todo():
    return render_template('todo.html', tasks=auth.get_user_todos(session['user_id']))

@app.route('/todo/add', methods=['POST'])
@login_required
def add_todo():
    auth.add_todo(session['user_id'], request.form.get('task'))
    return redirect(url_for('todo'))

@app.route('/todo/toggle/<int:task_id>')
@login_required
def toggle_todo(task_id):
    auth.toggle_todo(task_id, session['user_id'])
    return redirect(url_for('todo'))

if __name__ == '__main__':
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)
    # run in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)