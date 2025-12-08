# ==================== modules/transaction_module.py ====================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@transaction_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        category_id = request.form['category_id']
        date = request.form['date']
        amount = float(request.form['amount'])
        transaction_type = request.form['type']
        description = request.form['description']
        
        # Make expenses negative
        if transaction_type == 'expense':
            amount = -abs(amount)
        else:
            amount = abs(amount)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO transactions (user_id, category_id, date, amount, description) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], category_id, date, amount, description)
        )
        db.commit()
        cursor.close()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get categories for dropdown
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories WHERE user_id = %s", (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()
    
    return render_template('add_transaction.html', categories=categories)

@transaction_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        category_id = request.form['category_id']
        date = request.form['date']
        amount = float(request.form['amount'])
        transaction_type = request.form['type']
        description = request.form['description']
        
        if transaction_type == 'expense':
            amount = -abs(amount)
        else:
            amount = abs(amount)
        
        cursor.execute(
            "UPDATE transactions SET category_id=%s, date=%s, amount=%s, description=%s WHERE id=%s AND user_id=%s",
            (category_id, date, amount, description, id, session['user_id'])
        )
        db.commit()
        cursor.close()
        
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    cursor.execute("SELECT * FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    transaction = cursor.fetchone()
    
    cursor.execute("SELECT * FROM categories WHERE user_id = %s", (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()
    
    return render_template('edit_transaction.html', transaction=transaction, categories=categories)

@transaction_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    cursor.close()
    
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


