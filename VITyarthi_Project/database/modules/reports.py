import mysql.connector
from datetime import datetime

class ReportGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def generate_weekly_report(self, uid):
        # Manual connection handling
        conn = mysql.connector.connect(**self.cfg)
        
        # Initialize defaults
        report = {
            'goals_updated': 0, 
            'study_sessions': 0, 
            'study_hours': 0, 
            'progress_logs': 0, 
            'average_marks': 0
        }

        try:
            cur = conn.cursor(dictionary=True)
            
            # 1. Goals (from activity logs)
            # UPDATED: uid, ts
            cur.execute("""
                SELECT count(*) as c FROM activity_logs 
                WHERE uid=%s 
                AND act_type='goal_updated' 
                AND ts >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """, (uid,))
            row = cur.fetchone()
            if row: report['goals_updated'] = row['c']

            # 2. Sessions
            # UPDATED: uid, duration_mins, sess_date
            cur.execute("""
                SELECT count(*) as c, sum(duration_mins) as m 
                FROM study_sessions 
                WHERE uid=%s 
                AND sess_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """, (uid,))
            row = cur.fetchone()
            report['study_sessions'] = row['c']
            
            # calc hours in python
            total_mins = row['m'] if row['m'] else 0
            report['study_hours'] = round(total_mins / 60, 1)

            # 3. Progress
            # UPDATED: marks, logged_at, uid, sid
            sql = """
                SELECT count(*) as c, avg(marks) as a 
                FROM progress_logs pl 
                JOIN subjects s ON pl.sid = s.sid 
                WHERE s.uid = %s AND pl.logged_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """
            cur.execute(sql, (uid,))
            res = cur.fetchone()
            report['progress_logs'] = res['c']
            report['average_marks'] = round(res['a'], 2) if res['a'] else 0

            return report
            
        except Exception as e:
            print(f"Weekly report error: {e}") 
            return report 
        finally:
            conn.close()

    def generate_monthly_report(self, user_id):
        # Using Context Manager style
        data = {
            'goals_completed': 0,
            'study_hours': 0,
            'average_marks': 0,
            'progress_logs': 0,
            'badges_earned': 0
        }
        
        with mysql.connector.connect(**self.cfg) as conn:
            with conn.cursor() as cur: # tuple cursor
                
                # Completed Goals
                # UPDATED: uid
                cur.execute("SELECT count(*) FROM goals WHERE uid=%s AND status='Completed' AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)", (user_id,))
                data['goals_completed'] = cur.fetchone()[0]

                # Time
                # UPDATED: duration_mins, sess_date, uid
                cur.execute("SELECT sum(duration_mins) FROM study_sessions WHERE uid=%s AND sess_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)", (user_id,))
                mins = cur.fetchone()[0]
                data['study_hours'] = round(mins/60, 1) if mins else 0.0

                # Marks
                # UPDATED: marks, logged_at, sid, uid
                cur.execute("""
                    SELECT avg(marks), count(*) 
                    FROM progress_logs pl JOIN subjects s ON pl.sid=s.sid 
                    WHERE s.uid=%s AND pl.logged_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """, (user_id,))
                row = cur.fetchone()
                data['average_marks'] = round(row[0], 2) if row[0] else 0
                data['progress_logs'] = row[1]

                # Badges
                # UPDATED: uid, earned_on
                cur.execute("SELECT count(*) FROM badges WHERE uid=%s AND earned_on >= DATE_SUB(NOW(), INTERVAL 30 DAY)", (user_id,))
                data['badges_earned'] = cur.fetchone()[0]

        return data

    def generate_subject_summary(self, uid):
        conn = mysql.connector.connect(**self.cfg)
        cur = conn.cursor(dictionary=True)
        
        # UPDATED: 
        # s.name -> subject_name
        # pl.marks -> marks_scored
        # ss.duration_mins -> study_minutes
        # s.sid, pl.sid, ss.sid
        q = """
            SELECT s.name as subject_name,
                   COUNT(DISTINCT pl.log_id) as total_logs,
                   AVG(pl.marks) as avg_marks,
                   MAX(pl.marks) as max_marks,
                   MIN(pl.marks) as min_marks,
                   SUM(ss.duration_mins) as study_minutes
            FROM subjects s
            LEFT JOIN progress_logs pl ON s.sid = pl.sid
            LEFT JOIN study_sessions ss ON s.sid = ss.sid
            WHERE s.uid = %s
            GROUP BY s.sid
            HAVING total_logs > 0
            ORDER BY s.name ASC
        """
        
        try:
            cur.execute(q, (uid,))
            rows = cur.fetchall()
            
            # formatting loop
            for r in rows:
                if r['avg_marks'] is None: r['avg_marks'] = 0
                else: r['avg_marks'] = round(r['avg_marks'], 2)
                
                m = r['study_minutes'] or 0
                r['study_hours'] = round(m / 60, 1)
                
            return rows
        except Exception as e:
            print(f"Summary error: {e}")
            return []
        finally:
            conn.close()