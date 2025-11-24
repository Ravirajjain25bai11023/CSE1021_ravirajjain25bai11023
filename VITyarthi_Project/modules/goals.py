import mysql.connector
from datetime import datetime, timedelta

class GoalManager:
    def __init__(self, config):
        self.cfg = config

    def _db(self):
        return mysql.connector.connect(**self.cfg)

    def create_goal(self, uid, subject, score, deadline, description=''):
        conn = self._db()
        cur = conn.cursor()
        
        # UPDATED: using 'uid', 'due_date', 'progress' (DB columns)
        # Default progress is 0
        sql = """
            INSERT INTO goals 
            (uid, subject, target_score, due_date, progress, status, description, created_at) 
            VALUES (%s, %s, %s, %s, 0, 'Pending', %s, NOW())
        """
        
        try:
            cur.execute(sql, (uid, subject, score, deadline, description))
            conn.commit()
            return {'success': True}
        except Exception as e:
            print(f"Create Goal Error: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            cur.close()
            conn.close()

    def get_user_goals(self, user_id):
        conn = self._db()
        cur = conn.cursor(dictionary=True)
        
        # UPDATED: Aliasing columns so the HTML templates don't break
        # DB Name -> Template Name
        # gid -> id
        # uid -> user_id
        # progress -> current_progress
        # due_date -> deadline
        query = """
            SELECT 
                gid as id, 
                uid as user_id, 
                subject, 
                target_score, 
                progress as current_progress, 
                status, 
                due_date as deadline, 
                description, 
                created_at 
            FROM goals 
            WHERE uid = %s
        """
        
        cur.execute(query, (user_id,))
        rows = cur.fetchall()
        conn.close()

        # sort manually in python because why not
        rows.sort(key=lambda x: x['created_at'], reverse=True)
        
        # quick status sync check
        for r in rows:
            self._sync_status(r)
        
        return rows

    def update_goal_progress(self, goal_id, uid, progress):
        conn = self._db()
        cur = conn.cursor()
        
        # Check existence using new column names
        cur.execute("SELECT gid FROM goals WHERE gid=%s AND uid=%s", (goal_id, uid))
        if not cur.fetchone():
            conn.close()
            return {'success': False, 'message': 'Not found'}

        try:
            p = int(progress)
            new_stat = 'Pending'
            if p > 0: new_stat = 'In Progress'
            if p >= 100: new_stat = 'Completed'

            # Update using DB column names (progress, status, gid)
            q = "UPDATE goals SET progress=%s, status=%s WHERE gid=%s"
            cur.execute(q, (p, new_stat, goal_id))
            conn.commit()
            
            return {'success': True}
            
        except ValueError:
            return {'success': False, 'message': 'Invalid number'}
        except Exception as e:
            print(f"Update error: {e}")
            return {'success': False, 'message': 'Database error'}
        finally:
            conn.close()

    def _sync_status(self, goal_row):
        # Helper to keep UI consistent
        p = goal_row['current_progress'] # using the alias from get_user_goals
        s = goal_row['status']
        
        real_s = 'Pending'
        if p >= 100: real_s = 'Completed'
        elif p > 0: real_s = 'In Progress'
        
        if s != real_s:
            goal_row['status'] = real_s 

    def delete_goal(self, gid, uid):
        conn = self._db()
        try:
            cur = conn.cursor()
            # 1. Delete logs (gid is foreign key)
            cur.execute("DELETE FROM progress_logs WHERE gid=%s", (gid,))
            
            # 2. Delete goal
            cur.execute("DELETE FROM goals WHERE gid=%s AND uid=%s", (gid, uid))
            conn.commit()
            return {'success': True}
        except Exception as e:
            print(e)
            conn.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    def get_user_stats(self, uid):
        # Re-using the get_user_goals logic to get the data
        # then processing in Python (inefficient but safe)
        goals = self.get_user_goals(uid)
        
        total = len(goals)
        if total == 0:
            return {
                'total_goals': 0, 'completed_goals': 0,
                'in_progress_goals': 0, 'average_progress': 0
            }

        done = 0
        active = 0
        prog_sum = 0
        
        for g in goals:
            st = g['status']
            prog_sum += g['current_progress']
            if st == 'Completed': done += 1
            if st == 'In Progress': active += 1

        return {
            'total_goals': total,
            'completed_goals': done,
            'in_progress_goals': active,
            'average_progress': round(prog_sum / total, 2)
        }

    def get_upcoming_deadlines(self, uid, days=7):
        # Filter in python to avoid dealing with SQL date diffs
        all_goals = self.get_user_goals(uid)
        
        limit = datetime.now().date() + timedelta(days=days)
        today = datetime.now().date()
        
        upcoming = []
        for g in all_goals:
            if g['status'] == 'Completed': continue
            
            d = g['deadline'] # using aliased name
            if isinstance(d, datetime): d = d.date()
            
            if today <= d <= limit:
                upcoming.append(g)
                
        upcoming.sort(key=lambda x: x['deadline'])
        return upcoming