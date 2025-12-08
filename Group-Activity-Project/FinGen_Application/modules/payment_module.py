# ==================== modules/payment_module.py ====================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db

payment_bp = Blueprint('payment', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@payment_bp.route('/')
@login_required
def list_payments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments WHERE user_id = %s ORDER BY payment_date DESC", (session['user_id'],))
    payments = cursor.fetchall()
    cursor.close()
    
    return render_template('payment.html', payments=payments)

@payment_bp.route('/add', methods=['POST'])
@login_required
def add():
    amount = float(request.form['amount'])
    description = request.form['description']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO payments (user_id, amount, description, status) VALUES (%s, %s, %s, 'unpaid')",
        (session['user_id'], amount, description)
    )
    db.commit()
    cursor.close()
    
    flash('Payment added successfully!', 'success')
    return redirect(url_for('payment.list_payments'))

@payment_bp.route('/mark_paid/<int:id>')
@login_required
def mark_paid(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE payments SET status = 'paid' WHERE id = %s AND user_id = %s",
        (id, session['user_id'])
    )
    db.commit()
    cursor.close()
    
    flash('Payment marked as paid!', 'success')
    return redirect(url_for('payment.list_payments'))

@payment_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM payments WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    cursor.close()
    
    flash('Payment deleted successfully!', 'success')
    return redirect(url_for('payment.list_payments'))