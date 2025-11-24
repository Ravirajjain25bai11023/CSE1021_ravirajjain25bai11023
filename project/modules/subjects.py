import mysql.connector
from datetime import datetime

class SubjectManager:
    def __init__(self, conf):
        self.conf = conf

    def create_subject(self, uid, name):
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor()
        
        # UPDATED: 'name' and 'uid'
        cur.execute("SELECT sid FROM subjects WHERE uid=%s AND name=%s", (uid, name))
        if cur.fetchone():
            conn.close()
            return {'success': False, 'message': 'Subject exists'}

        try:
            # UPDATED: 'added_on' instead of 'created_at'
            cur.execute("INSERT INTO subjects (uid, name, added_on) VALUES (%s, %s, NOW())", (uid, name))
            conn.commit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    def get_user_subjects(self, uid):
        # UPDATED: Mapping DB columns (sid, name) -> Template variables (id, subject_name)
        with mysql.connector.connect(**self.conf) as conn:
            with conn.cursor(dictionary=True) as cur:
                sql = """
                    SELECT sid as id, uid as user_id, name as subject_name, added_on as created_at 
                    FROM subjects 
                    WHERE uid = %s 
                    ORDER BY name ASC
                """
                cur.execute(sql, (uid,))
                return cur.fetchall()

    def get_user_subjects_with_progress(self, uid):
        # This query joins subjects, logs, and goals
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor(dictionary=True)
        
        # UPDATED: heavy aliasing to match template expectations
        # subjects: sid -> id, name -> subject_name
        # progress_logs: marks -> marks_scored
        # goals: progress -> current_progress
        sql = """
            SELECT s.sid as id, 
                   s.name as subject_name,
                   COUNT(DISTINCT pl.log_id) as total_logs,
                   SUM(pl.marks) as total_marks,
                   AVG(pl.marks) as avg_marks,
                   g.target_score,
                   g.progress as current_progress
            FROM subjects s
            LEFT JOIN progress_logs pl ON s.sid = pl.sid
            LEFT JOIN goals g ON g.subject = s.name AND g.uid = s.uid
            WHERE s.uid = %s
            GROUP BY s.sid
            ORDER BY s.name ASC
        """
        
        try:
            cur.execute(sql, (uid,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            print(f"Subj Progress Error: {e}")
            return [] 
        finally:
            conn.close()

    def log_subject_progress(self, sid, uid, marks, notes=''):
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor()
        
        # 1. check ownership
        cur.execute("SELECT sid FROM subjects WHERE sid=%s AND uid=%s", (sid, uid))
        if not cur.fetchone():
            conn.close()
            return {'success': False, 'message': 'Invalid subject'}

        # 2. find goal link (if any)
        cur.execute("""
            SELECT g.gid FROM goals g 
            JOIN subjects s ON g.subject = s.name 
            WHERE s.sid = %s AND g.uid = %s
        """, (sid, uid))
        
        row = cur.fetchone()
        gid = row[0] if row else None

        # 3. log it (using new column names: marks, logged_at)
        try:
            cur.execute(
                "INSERT INTO progress_logs (gid, sid, marks, logged_at, notes) VALUES (%s, %s, %s, NOW(), %s)",
                (gid, sid, marks, notes)
            )
            conn.commit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    def get_subject_progress_history(self, sid, uid):
        with mysql.connector.connect(**self.conf) as conn:
            with conn.cursor(dictionary=True) as cur:
                # Aliasing for consistency
                q = """
                    SELECT pl.log_id as id, pl.marks as marks_scored, pl.logged_at as date_logged, pl.notes, 
                           s.name as subject_name 
                    FROM progress_logs pl
                    JOIN subjects s ON pl.sid = s.sid
                    WHERE pl.sid = %s AND s.uid = %s
                    ORDER BY pl.logged_at DESC
                """
                cur.execute(q, (sid, uid))
                return cur.fetchall()

    def log_study_session(self, uid, sid, mins):
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor()
        
        try:
            # UPDATED: duration_mins, sess_date
            cur.execute(
                "INSERT INTO study_sessions (uid, sid, duration_mins, sess_date) VALUES (%s, %s, %s, NOW())",
                (uid, sid, mins)
            )
            conn.commit()
            
            # Check for badge (Study Pro)
            cur.execute("SELECT SUM(duration_mins) FROM study_sessions WHERE uid=%s", (uid,))
            res = cur.fetchone()
            total = res[0] if res and res[0] else 0
            
            if total >= 3000: # 50 hours
                from modules.auth import AuthManager
                am = AuthManager(self.conf)
                am.award_badge(uid, 'Study Pro', 'achievement')

            return {'success': True}
        except Exception as e:
            print(f"Study Log Error: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    def get_study_time_stats(self, uid):
        stats = {'total_hours': 0, 'weekly_hours': 0}
        
        with mysql.connector.connect(**self.conf) as conn:
            with conn.cursor() as cur:
                # Total
                cur.execute("SELECT sum(duration_mins) FROM study_sessions WHERE uid=%s", (uid,))
                row = cur.fetchone()
                if row and row[0]:
                    stats['total_hours'] = round(row[0] / 60, 1)

                # Weekly
                cur.execute("""
                    SELECT sum(duration_mins) FROM study_sessions 
                    WHERE uid=%s AND sess_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                """, (uid,))
                row = cur.fetchone()
                if row and row[0]:
                    stats['weekly_hours'] = round(row[0] / 60, 1)
                    
        return stats