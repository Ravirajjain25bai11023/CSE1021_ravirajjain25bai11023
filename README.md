# 📚 Student Academic Goal & Progress Tracker

## Overview of the Project
Let’s be real: keeping track of grades, study hours, and deadlines usually involves a mess of sticky notes or a chaotic Excel sheet. I built **Student Tracker** to fix that.

This is a dedicated, self-hosted web application designed to manage your academic life. It helps you set goals, visualize your progress with auto-generated charts, and even gamifies the process to keep you motivated. No heavy frontend frameworks here—just solid Python, clean HTML/CSS, and data visualization that actually works.

---

## Features
It’s not just a simple to-do list. Here is what the application handles:

* **Goal Management:** Set target scores and deadlines. The app tracks your status (Pending → In Progress → Completed) automatically based on your logs.
* **Dashboard Analytics:** I used **Matplotlib** to generate dynamic charts. You get visual feedback on your weekly progress and subject performance right on the dashboard.
* **Subject Tracking:** Keep a log of every subject you are studying and record your marks to see averages over time.
* **Gamification System:** Earn badges (like "Week Warrior" or "Consistency King") for maintaining login streaks and hitting your goals.
* **Study Timer:** A built-in Pomodoro timer (standard 25-min sessions) to help you focus without leaving the app.
* **Reports & Exports:** You can download your weekly progress as CSV files or export your entire data history as a ZIP file.
* **Secure Authentication:** Full registration and login system with hashed passwords, so your data stays private.

---

## Technologies & Tools Used
I kept the stack modular and lightweight to make it easy to deploy and modify.

* **Backend:** Python 3.8+ (Flask 2.3.3)
* **Database:** MySQL 8.0+
* **Frontend:** HTML5, CSS3 (Custom design, no external frameworks)
* **Visualization:** Matplotlib 3.7.2 (Server-side chart rendering)
* **Database Connector:** `mysql-connector-python`

---

## Steps to Install & Run the Project

Follow these steps to get the app running on your local machine.

### 1. Prerequisites
Ensure you have Python and MySQL installed:
```bash
python --version  # Should be 3.8 or higher
mysql --version   # Should be 8.0 or higher
````

### 2\. Clone the Repository

Download the project files and navigate into the folder:

```bash
git clone <your-repo-url>
cd student_tracker
```

### 3\. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4\. Database Setup

1.  Log in to your MySQL server:
    ```bash
    mysql -u root -p
    ```
2.  Create the database using the provided schema file:
    ```sql
    SOURCE database/schema.sql;
    ```
3.  **Critical Step:** Open `app.py` (lines 17-22) and update the `DB_CONFIG` dictionary with your actual MySQL password:
    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'YOUR_ACTUAL_PASSWORD',  # Update this!
        'database': 'student_tracker_db'
    }
    ```

### 5\. Create Required Folders

The app needs specific folders to save charts and exports. Create them if they don't exist:

```bash
mkdir -p static/charts
mkdir -p exports
```

### 6\. Run the Application

```bash
python app.py
```

You should see a message saying "Running on http://0.0.0.0:5000". Open that URL in your browser.

-----

## Instructions for Testing

Once the app is running, follow this quick "sanity check" to ensure all modules are working correctly:

1.  **Test Registration:** Go to the Sign-Up page and create a new account. If successful, you should be redirected to the Dashboard.
2.  **Add Data:**
      * Navigate to **"Subjects"** and add a new subject (e.g., "Mathematics").
      * Go to **"My Goals"** and create a goal for that subject (e.g., "Score 90% in Finals").
3.  **Verify Charts:**
      * Go to **"Subject Tracking"** and log a test score (e.g., 85).
      * Return to the **Dashboard**. You should see a chart generated showing this data. (If the image is broken, check the `static/charts` folder permissions).
4.  **Test Tools:**
      * Open the **Study Timer** and start a 5-minute session to see if the countdown works.
      * Go to **Reports** and click "Export Goals" to verify that a CSV file downloads.

-----

## Screenshots

*The main dashboard showing progress charts and upcoming deadlines.*

*The goal management interface.*

```
```
