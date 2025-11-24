import csv
import os
import zipfile
import mysql.connector
from datetime import datetime

class DataExporter:
    def __init__(self, cfg):
        self.cfg = cfg
        # check folder
        if not os.path.exists('static/exports'):
            os.makedirs('static/exports')

    def _get_conn(self):
        return mysql.connector.connect(**self.cfg)

    def export_goals_csv(self, uid):
        # Manual CSV writing (string manipulation) instead of csv lib
        # This breaks the pattern completely
        tstamp = datetime.now().strftime("%Y%m%d")
        fname = f'static/exports/goals_{uid}_{tstamp}.csv'
        
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            # using aliases to match old schema if needed
            q = "SELECT subject, target_score, progress, status, due_date FROM goals WHERE uid = %s"
            cur.execute(q, (uid,))
            data = cur.fetchall()
            
            with open(fname, 'w') as f:
                # write header
                f.write("Subject,Target,Progress,Status,Deadline\n")
                for row in data:
                    # manual string formatting
                    line = f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]}\n"
                    f.write(line)
            return fname
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
        finally:
            conn.close()

    def export_progress_csv(self, uid):
        # Standard CSV lib usage here
        f_path = os.path.join('static/exports', f'progress_{uid}.csv')
        
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                # join query
                sql = """
                    SELECT s.name, p.marks, p.logged_at, p.notes
                    FROM progress_logs p
                    JOIN subjects s ON p.sid = s.sid
                    WHERE s.uid = %s
                    ORDER BY p.logged_at DESC
                """
                cur.execute(sql, (uid,))
                rows = cur.fetchall()

        # writing file outside db context
        with open(f_path, 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(['Subject', 'Marks', 'Date', 'Notes'])
            for r in rows:
                d = r[2].strftime('%Y-%m-%d')
                w.writerow([r[0], r[1], d, r[3]])
                
        return f_path

    def export_reports_csv(self, uid):
        # DictWriter approach for variation
        out = f'static/exports/summary_{uid}.csv'
        
        conn = self._get_conn()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT s.name, AVG(p.marks) as avg, COUNT(p.log_id) as cnt
            FROM subjects s
            LEFT JOIN progress_logs p ON s.sid = p.sid
            WHERE s.uid = %s GROUP BY s.sid
        """, (uid,))
        
        res = cur.fetchall()
        conn.close()

        with open(out, 'w', newline='') as f:
            # simpler header
            f.write("Subject,Avg Marks,Log Count\n")
            for r in res:
                # handling nulls inline
                a = round(r['avg'], 2) if r['avg'] else 0
                f.write(f"{r['name']},{a},{r['cnt']}\n")
                
        return out

    def export_all_data(self, uid):
        # Zip everything
        z_path = f'static/exports/student_data_{uid}.zip'
        
        # get files
        files = []
        f1 = self.export_goals_csv(uid)
        if f1: files.append(f1)
        
        f2 = self.export_progress_csv(uid)
        if f2: files.append(f2)
        
        f3 = self.export_reports_csv(uid)
        if f3: files.append(f3)
        
        if not files: return None
        
        try:
            with zipfile.ZipFile(z_path, 'w') as z:
                for f in files:
                    z.write(f, os.path.basename(f))
            return z_path
        except:
            return None