# ==================== modules/report_module.py ====================
from flask import Blueprint, render_template, session, redirect, url_for
from database import get_db
import json

report_bp = Blueprint('report', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@report_bp.route('/')
@login_required
def view():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Category-wise spending (expenses only)
    cursor.execute("""
        SELECT c.name, SUM(ABS(t.amount)) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s AND t.amount < 0
        GROUP BY c.name
    """, (session['user_id'],))
    category_data = cursor.fetchall()
    
    # Monthly spending
    cursor.execute("""
        SELECT DATE_FORMAT(date, '%%Y-%%m') as month, 
               SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses,
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income
        FROM transactions
        WHERE user_id = %s
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """, (session['user_id'],))
    monthly_data = cursor.fetchall()
    
    cursor.close()
    
    # Prepare data for Chart.js
    categories = [item['name'] for item in category_data]
    amounts = [float(item['total']) for item in category_data]
    
    months = [item['month'] for item in monthly_data]
    expenses = [float(item['expenses']) for item in monthly_data]
    income = [float(item['income']) for item in monthly_data]
    
    return render_template('report.html',
                         categories=json.dumps(categories),
                         amounts=json.dumps(amounts),
                         months=json.dumps(months),
                         expenses=json.dumps(expenses),
                         income=json.dumps(income))
