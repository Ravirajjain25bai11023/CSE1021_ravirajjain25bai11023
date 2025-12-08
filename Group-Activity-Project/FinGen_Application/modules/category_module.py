# ==================== modules/category_module.py ====================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db

category_bp = Blueprint('category', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@category_bp.route('/')
@login_required
def list_categories():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories WHERE user_id = %s", (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()
    
    return render_template('categories.html', categories=categories)

@category_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form['name']
    cat_type = request.form['type']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s)",
        (session['user_id'], name, cat_type)
    )
    db.commit()
    cursor.close()
    
    flash('Category added successfully!', 'success')
    return redirect(url_for('category.list_categories'))

@category_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM categories WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    cursor.close()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('category.list_categories'))
