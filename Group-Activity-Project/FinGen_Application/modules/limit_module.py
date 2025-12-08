# ==================== modules/limit_module.py ====================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db

limit_bp = Blueprint('limit', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@limit_bp.route('/')
@login_required
def view():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM spending_limits WHERE user_id = %s", (session['user_id'],))
    limit_data = cursor.fetchone()
    
    cursor.execute("""
        SELECT COALESCE(SUM(ABS(amount)), 0) as today_spending 
        FROM transactions 
        WHERE user_id = %s AND DATE(date) = CURDATE() AND amount < 0
    """, (session['user_id'],))
    today = cursor.fetchone()
    
    cursor.close()
    
    return render_template('limit.html', limit_data=limit_data, today_spending=today['today_spending'])

@limit_bp.route('/update', methods=['POST'])
@login_required
def update():
    daily_limit = float(request.form['daily_limit'])
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE spending_limits SET daily_limit = %s WHERE user_id = %s",
        (daily_limit, session['user_id'])
    )
    db.commit()
    cursor.close()
    
    flash('Daily limit updated successfully!', 'success')
    return redirect(url_for('limit.view'))

@limit_bp.route('/borrow', methods=['POST'])
@login_required
def borrow():
    borrow_amount = float(request.form['borrow_amount'])
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE spending_limits SET borrowed_amount = borrowed_amount + %s WHERE user_id = %s",
        (borrow_amount, session['user_id'])
    )
    db.commit()
    cursor.close()
    
    flash(f'Borrowed ${borrow_amount} from future limit!', 'success')
    return redirect(url_for('limit.view'))


