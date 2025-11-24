# 📚 Student Tracker

**A self-hosted academic dashboard built with Flask & MySQL.**

Let’s be real: keeping track of grades, study hours, and deadlines usually involves a mess of sticky notes or a chaotic Excel sheet. I built **Student Tracker** to fix that. It’s a dedicated web app to manage your academic life, visualize your progress, and maybe even make studying a little less painful with some gamification.

No heavy frontend frameworks here—just solid Python, clean HTML/CSS, and data visualization that works.

-----

## 🧐 What can it do?

It’s not just a to-do list. Here are the main tools included:

  * **Goal Management:** Set target scores for your subjects and track them. The app auto-updates the status (Pending → In Progress → Completed) based on your inputs.
  * **Analytics Dashboard:** I used **Matplotlib** to auto-generate charts. You get immediate visual feedback on your weekly progress, subject performance, and goal completion.
  * **Study Timer (Pomodoro):** A built-in focus timer. You can do standard 25-minute sprints or customize it.
  * **Gamification:** You earn badges (like "Week Warrior" or "Consistency King") for maintaining streaks and hitting goals. It helps keep the motivation up.
  * **Reports & Exports:** Need to back up your data? You can export your logs to CSV or download a full ZIP archive of your semester performance.
  * **Privacy:** It includes a full registration/login system. Your data is isolated to your account.

-----

## 🛠 Under the Hood

The stack is kept simple and modular. Great for learning how full-stack apps fit together.

  * **Backend:** Python 3.8+ (Flask 2.3.3)
  * **Database:** MySQL 8.0+
  * **Frontend:** HTML5, CSS3 (Custom styling, no Bootstrap/Tailwind dependency)
  * **Visualization:** Matplotlib (Server-side rendering)
  * **ORM/Connector:** `mysql-connector-python`

-----

## 🚀 Getting Started

Follow these steps to get the app running locally.

### 1\. Prerequisites

You need Python and MySQL installed.

```bash
python --version  # Should be 3.8+
mysql --version   # Should be 8.0+
```

### 2\. Clone and Install

Grab the repo and install the Python packages.

```bash
git clone [your-repo-link-here]
cd student_tracker
pip install -r requirements.txt
```

### 3\. Database Setup

This is the most critical part. Make sure your MySQL server is running.

1.  Log into MySQL: `mysql -u root -p`
2.  Create the database using the provided schema:
    ```sql
    SOURCE database/schema.sql;
    ```
3.  **Important:** Open `app.py` (lines 17-22) and update the `DB_CONFIG` dictionary with your actual MySQL password.

<!-- end list -->

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_ACTUAL_PASSWORD_HERE', # Don't forget this!
    'database': 'student_tracker_db'
}
```

### 4\. Create Static Folders

Sometimes empty folders don't get pushed to Git. The app needs these to save the generated charts and exports, or it will crash.

```bash
mkdir -p static/charts
mkdir -p exports
```

### 5\. Run it

```bash
python app.py
```

Head over to `http://localhost:5000`.

-----

## 📂 Project Layout

If you want to tweak the code, here is where everything lives:

  * `app.py`: The entry point. Handles routing and app config.
  * `modules/`: I separated the logic here so `app.py` doesn't get huge.
      * `auth.py`: Login/Register logic.
      * `charts.py`: The Matplotlib code that generates the PNGs.
      * `goals.py` & `subjects.py`: CRUD operations.
  * `templates/`: Standard Jinja2 templates.
  * `static/css/style.css`: All the custom styling is here.

-----

## 🐛 Common Issues (Troubleshooting)

**"Access denied for user 'root'..."**

  * 99% of the time, this means you didn't update the password in `app.py` or your MySQL server isn't running.

**"ModuleNotFoundError"**

  * You skipped the `pip install` step. Run `pip install -r requirements.txt`.

**Charts aren't showing up?**

  * Check if the `static/charts` folder exists. The app needs write permissions there to save the images.

**Port 5000 is busy?**

  * If you have another Flask app running, change the last line in `app.py` to `app.run(port=5001)`.

--
