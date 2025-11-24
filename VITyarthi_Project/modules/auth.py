import mysql.connector
import hashlib
from datetime import datetime, timedelta

# Defined at module level
BADGE_CONFIG = [
    {'name': '3-Day Streak', 'type': 'streak', 'desc': 'Login for 3 consecutive days'},
    {'name': 'Week Warrior', 'type': 'streak', 'desc': 'Login for 7 consecutive days'},
    {'name': 'Consistency King', 'type': 'streak', 'desc': 'Login for 30 consecutive days'},
    {'name': 'Goal Master', 'type': 'achievement', 'desc': 'Complete your first goal'},
    {'name': 'Deadline Champion', 'type': 'achievement', 'desc': 'Complete 5 goals before deadline'},
    {'name': 'Study Pro', 'type': 'achievement', 'desc': 'Log 50 hours of study time'}
]

class AuthManager:
    def __init__(self, db_conf):
        self.conf = db_conf
        # simple salt
        self._salt = "somesecurestring2024"

    def _get_db(self):
        return mysql.connector.connect(**self.conf)

    def _hash(self, raw_pwd):
        return hashlib.sha256((raw_pwd + self._salt).encode()).hexdigest()

    def register_user(self, user, email, pwd):
        try:
            with self._get_db() as conn:
                with conn.cursor() as cur:
                    # UPDATED COLUMN NAMES HERE:
                    # pwd_hash, joined_at, streak (instead of password_hash, created_at, study_streak)
                    q = """INSERT INTO users 
                           (username, email, pwd_hash, joined_at, last_login, streak) 
                           VALUES (%s, %s, %s, %s, %s, 0)"""
                    
                    cur.execute(q, (user, email, self._hash(pwd), datetime.now(), datetime.now()))
                    conn.commit()
                    
                    return {'success': True, 'message': 'Registration successful'}

        except mysql.connector.Error as err:
            # Handle duplicate entries
            if err.errno == 1062:
                msg = str(err)
                if 'email' in msg:
                    return {'success': False, 'message': 'Email already registered'}
                if 'username' in msg:
                    return {'success': False, 'message': 'Username taken'}
            return {'success': False, 'message': f"DB Error: {err}"}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def login_user(self, email, pwd):
        try:
            with self._get_db() as conn:
                with conn.cursor(dictionary=True) as cur:
                    h_pwd = self._hash(pwd)
                    
                    # UPDATED: using uid and pwd_hash
                    cur.execute("SELECT uid, username FROM users WHERE email = %s AND pwd_hash = %s", (email, h_pwd))
                    row = cur.fetchone()
                    
                    if not row:
                        return {'success': False, 'message': 'Invalid credentials'}

                    # Update access log
                    cur.execute("UPDATE users SET last_login = %s WHERE uid = %s", (datetime.now(), row['uid']))
                    conn.commit()
                    
                    return {
                        'success': True, 
                        'user_id': row['uid'], # Mapping uid to user_id for session
                        'username': row['username']
                    }
        except Exception as e:
            print(f"Login failed: {e}")
            return {'success': False, 'message': 'System error during login'}

    def update_streak(self, uid):
        try:
            with self._get_db() as conn:
                with conn.cursor(dictionary=True) as cur:
                    # UPDATED: using streak and uid
                    cur.execute("SELECT last_login, streak FROM users WHERE uid = %s", (uid,))
                    row = cur.fetchone()
                    
                    if not row: return

                    last_date = row['last_login'].date() if isinstance(row['last_login'], datetime) else row['last_login']
                    today = datetime.now().date()
                    diff = (today - last_date).days
                    
                    curr_streak = row['streak']
                    new_streak = curr_streak

                    if diff == 1:
                        new_streak += 1
                        self._check_streak_badges(uid, new_streak)
                    elif diff > 1:
                        new_streak = 1 # Reset
                    
                    if diff != 0: 
                        cur.execute("UPDATE users SET streak = %s WHERE uid = %s", (new_streak, uid))
                        conn.commit()

        except Exception as e:
            print(f"[Streak Error] {e}")

    def _check_streak_badges(self, uid, days):
        milestones = {3: '3-Day Streak', 7: 'Week Warrior', 30: 'Consistency King'}
        if days in milestones:
            self.award_badge(uid, milestones[days], 'streak')

    def award_badge(self, uid, name, b_type):
        try:
            with self._get_db() as conn:
                with conn.cursor() as cur:
                    # UPDATED: earned_on instead of earned_date (from SQL schema)
                    q = "INSERT IGNORE INTO badges (user_id, badge_name, type, earned_on) VALUES (%s, %s, %s, %s)"
                    cur.execute(q, (uid, name, b_type, datetime.now()))
                    conn.commit()
        except Exception:
            pass 

    def get_streak_info(self, uid):
        with self._get_db() as conn:
            with conn.cursor(dictionary=True) as cur:
                # UPDATED: streak vs study_streak
                cur.execute("SELECT streak as study_streak, last_login FROM users WHERE uid = %s", (uid,))
                res = cur.fetchone()
                return res if res else {'study_streak': 0, 'last_login': datetime.now()}

    def log_activity(self, uid, act_type, desc):
        try:
            with self._get_db() as conn:
                with conn.cursor() as cur:
                    # UPDATED: act_type and ts
                    cur.execute(
                        "INSERT INTO activity_logs (uid, act_type, details, ts) VALUES (%s, %s, %s, %s)",
                        (uid, act_type, desc, datetime.now())
                    )
                    conn.commit()
        except Exception as e: 
            print(e)

    def get_recent_activities(self, uid, limit=10):
        with self._get_db() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Map DB columns back to what template expects
                cur.execute("""
                    SELECT act_type as activity_type, details as description, ts as timestamp 
                    FROM activity_logs 
                    WHERE uid = %s ORDER BY ts DESC LIMIT %s
                """, (uid, limit))
                return cur.fetchall()

    def get_user_badges(self, uid):
        with self._get_db() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Map earned_on to earned_date for template compatibility
                cur.execute("SELECT badge_name, earned_on as earned_date, type FROM badges WHERE uid = %s ORDER BY earned_on DESC", (uid,))
                return cur.fetchall()

    def get_available_badges(self):
        return BADGE_CONFIG

    def get_user_info(self, uid):
        with self._get_db() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Map columns for profile page
                cur.execute("SELECT username, email, joined_at as created_at, streak as study_streak FROM users WHERE uid = %s", (uid,))
                return cur.fetchone()

    def get_user_todos(self, uid):
        with self._get_db() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Map columns: task -> task_description, is_done -> completed
                cur.execute("SELECT tid as id, task as task_description, is_done as completed, created_at FROM todo_tasks WHERE uid = %s ORDER BY created_at DESC", (uid,))
                return cur.fetchall()

    def add_todo(self, uid, task):
        try:
            with self._get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO todo_tasks (uid, task, is_done, created_at) VALUES (%s, %s, 0, %s)",
                        (uid, task, datetime.now())
                    )
                    conn.commit()
                    return {'success': True}
        except Exception:
            return {'success': False}

    def toggle_todo(self, task_id, uid):
        try:
            with self._get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE todo_tasks SET is_done = NOT is_done WHERE tid = %s AND uid = %s",
                        (task_id, uid)
                    )
                    conn.commit()
                    return {'success': True}
        except Exception:
            return {'success': False}