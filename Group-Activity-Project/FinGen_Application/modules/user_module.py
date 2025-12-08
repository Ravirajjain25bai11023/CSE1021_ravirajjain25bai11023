# ==================== modules/user_module.py ====================
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            db.commit()
            
            # Get user id and create default categories
            user_id = cursor.lastrowid
            default_categories = [
                ('Food', 'expense'), ('Travel', 'expense'), ('Bills', 'expense'),
                ('Shopping', 'expense'), ('Entertainment', 'expense'),
                ('Salary', 'income'), ('Freelance', 'income'), ('Other', 'income')
            ]
            
            for cat_name, cat_type in default_categories:
                cursor.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (%s, %s, %s)",
                    (user_id, cat_name, cat_type)
                )
            
            # Create default spending limit
            cursor.execute(
                "INSERT INTO spending_limits (user_id, daily_limit) VALUES (%s, 1000)",
                (user_id,)
            )
            
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
        finally:
            cursor.close()
    
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@user_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('user.login'))