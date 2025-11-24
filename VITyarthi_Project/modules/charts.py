import os
import mysql.connector
import matplotlib
matplotlib.use('Agg') # fix for server side errors
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class ChartGenerator:
    def __init__(self, db_config, folder):
        self.conf = db_config
        self.folder = folder
        
        # make sure path exists
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        plt.style.use('seaborn-v0_8-darkgrid')

    def generate_goal_completion_chart(self, user_id):
        # Using default cursor (tuples) here
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor()
        
        try:
            # UPDATED: user_id -> uid
            cur.execute("SELECT status, COUNT(*) FROM goals WHERE uid = %s GROUP BY status", (user_id,))
            rows = cur.fetchall()
        finally:
            conn.close() 

        if not rows: 
            return None

        # manual unpacking
        labels = []
        sizes = []
        for r in rows:
            labels.append(r[0])
            sizes.append(r[1])

        # pie chart
        plt.figure(figsize=(8, 6))
        colors = ['#ff6b6b', '#4ecdc4', '#95e1d3'] 
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Goal Status', fontweight='bold')
        
        # save it
        fname = f'goal_completion_{user_id}.png'
        path = os.path.join(self.folder, fname)
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        
        return path

    def generate_weekly_progress_chart(self, uid):
        # get last 7 days
        with mysql.connector.connect(**self.conf) as conn:
            with conn.cursor(dictionary=True) as cur:
                # UPDATED: 
                # - date_logged -> logged_at
                # - marks_scored -> marks
                # - subject_id -> sid
                # - user_id -> uid
                sql = """
                    SELECT DATE(logged_at) as dt, SUM(marks) as val
                    FROM progress_logs pl
                    JOIN subjects s ON pl.sid = s.sid
                    WHERE s.uid = %s 
                    AND logged_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    GROUP BY dt ORDER BY dt ASC
                """
                cur.execute(sql, (uid,))
                data = cur.fetchall()

        # handle empty data
        if not data:
            # generate dummy dates for empty graph
            dates = [(datetime.now() - timedelta(days=x)).strftime('%m/%d') for x in range(6, -1, -1)]
            vals = [0] * 7
        else:
            dates = [x['dt'].strftime('%m/%d') for x in data]
            vals = [x['val'] for x in data]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, vals, marker='o', color='#4ecdc4', linewidth=2)
        plt.fill_between(range(len(dates)), vals, alpha=0.3, color='#4ecdc4')
        
        plt.title('Weekly Trends')
        plt.ylabel('Total Marks')
        plt.grid(True, alpha=0.3)
        
        f_path = os.path.join(self.folder, f'weekly_progress_{uid}.png')
        plt.savefig(f_path, bbox_inches='tight')
        plt.close()
        return f_path

    def generate_subject_performance_chart(self, uid):
        # top 10 subjs
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor() # tuples again
        
        # UPDATED: 
        # - subject_name -> name
        # - marks_scored -> marks
        # - subject_id -> sid
        # - id -> sid
        # - user_id -> uid
        q = """
            SELECT s.name, AVG(pl.marks)
            FROM subjects s
            JOIN progress_logs pl ON s.sid = pl.sid
            WHERE s.uid = %s
            GROUP BY s.sid HAVING COUNT(pl.log_id) > 0
            ORDER BY 2 DESC LIMIT 10
        """
        cur.execute(q, (uid,))
        res = cur.fetchall()
        conn.close()

        if not res: return None

        names = [x[0][:15] for x in res]
        avgs = [float(x[1]) for x in res]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(names, avgs, color='#95e1d3')
        
        ax.bar_label(bars, fmt='%.1f', padding=3)
        ax.set_title('Subject Performance')
        
        out = os.path.join(self.folder, f'subject_performance_{uid}.png')
        plt.savefig(out, bbox_inches='tight')
        plt.close()
        return out

    def generate_monthly_comparison_chart(self, user_id):
        # UPDATED:
        # - date_logged -> logged_at
        # - marks_scored -> marks
        # - subject_id -> sid
        # - user_id -> uid
        sql = """
            SELECT DATE_FORMAT(logged_at, '%Y-%m') as m, 
                   COUNT(*) as cnt, AVG(marks) as score
            FROM progress_logs pl
            JOIN subjects s ON pl.sid = s.sid
            WHERE s.uid = %s AND logged_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY m ORDER BY m ASC
        """
        
        conn = mysql.connector.connect(**self.conf)
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows: return None

        months = [r['m'] for r in rows]
        
        # dual axis plot
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        c1 = '#4ecdc4'
        ax1.bar(months, [r['cnt'] for r in rows], color=c1, alpha=0.6, label='Logs')
        ax1.set_ylabel('Count', color=c1, fontweight='bold')
        
        ax2 = ax1.twinx()
        c2 = '#ff6b6b'
        ax2.plot(months, [r['score'] for r in rows], color=c2, marker='o', label='Avg')
        ax2.set_ylabel('Avg Score', color=c2, fontweight='bold')
        
        plt.title('Monthly Overview')
        fig.tight_layout()
        
        path = os.path.join(self.folder, f'monthly_comparison_{user_id}.png')
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path

    def generate_study_time_chart(self, uid):
        # UPDATED:
        # - subject_name -> name
        # - duration_minutes -> duration_mins
        # - subject_id -> sid
        # - user_id -> uid
        # - id -> sid
        with mysql.connector.connect(**self.conf) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.name, SUM(ss.duration_mins)
                FROM study_sessions ss
                JOIN subjects s ON ss.sid = s.sid
                WHERE ss.uid = %s
                GROUP BY s.sid ORDER BY 2 DESC LIMIT 10
            """, (uid,))
            data = cur.fetchall()

        if not data: return None

        # conv to hours
        hrs = []
        lbls = []
        for row in data:
            lbls.append(row[0])
            hrs.append(round(row[1]/60, 1))

        plt.figure(figsize=(8, 6))
        plt.pie(hrs, labels=lbls, autopct='%1.1f%%', startangle=90)
        plt.title('Study Hours')
        
        p = os.path.join(self.folder, f'study_time_{uid}.png')
        plt.savefig(p, bbox_inches='tight')
        plt.close()
        
        return p