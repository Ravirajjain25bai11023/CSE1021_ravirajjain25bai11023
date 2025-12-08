from flask import Flask, redirect, url_for, session, render_template
from database import init_app
from modules.user_module import user_bp
from modules.transaction_module import transaction_bp
from modules.category_module import category_bp
from modules.limit_module import limit_bp
from modules.report_module import report_bp
from modules.payment_module import payment_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize database
init_app(app)

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(transaction_bp, url_prefix='/transaction')
app.register_blueprint(category_bp, url_prefix='/category')
app.register_blueprint(limit_bp, url_prefix='/limit')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(payment_bp, url_prefix='/payment')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('user.login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    from database import get_db
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get transaction summary
    cursor.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(amount), 0) as total_amount 
        FROM transactions WHERE user_id = %s
    """, (session['user_id'],))
    transaction_summary = cursor.fetchone()
    
    # Get spending limit
    cursor.execute("""
        SELECT daily_limit, borrowed_amount 
        FROM spending_limits WHERE user_id = %s
    """, (session['user_id'],))
    limit_data = cursor.fetchone()
    
    # Get today's spending
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) as today_spending 
        FROM transactions 
        WHERE user_id = %s AND DATE(date) = CURDATE() AND amount < 0
    """, (session['user_id'],))
    today_spending = cursor.fetchone()
    
    cursor.close()
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         transaction_summary=transaction_summary,
                         limit_data=limit_data,
                         today_spending=abs(today_spending['today_spending']) if today_spending else 0)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
