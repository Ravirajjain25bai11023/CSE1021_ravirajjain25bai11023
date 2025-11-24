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
## Project Structure

```text
project/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── database/
│   └── schema.sql              # MySQL database schema
├── modules/
│   ├── __init__.py             # Module initialization
│   ├── auth.py                 # Authentication manager
│   ├── goals.py                # Goal management
│   ├── subjects.py             # Subject tracking
│   ├── reports.py              # Report generation
│   ├── charts.py               # Chart generation (Matplotlib)
│   └── exports.py              # Data export functions
├── static/
│   ├── css/
│   │   └── style.css           # Main stylesheet
│   └── charts/                 # Generated chart images
├── templates/
│   ├── base.html               # Base template
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Dashboard
│   ├── goals.html              # Goals management
│   ├── subjects.html           # Subjects tracking
│   ├── reports.html            # Reports page
│   ├── badges.html             # Badges & achievements
│   ├── profile.html            # User profile
│   ├── study_timer.html        # Pomodoro timer
│   └── todo.html               # To-do list
└── exports/                    # Generated export files

````
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
cd project
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

*The main dashboard showing progress.*

<img width="1918" height="912" alt="Screenshot 2025-11-24 165744" src="https://github.com/user-attachments/assets/ec5e04b7-dc0f-49c3-826e-82067636ac00" />

<img width="1919" height="914" alt="Screenshot 2025-11-24 165820" src="https://github.com/user-attachments/assets/de37da20-9097-4cc5-b5ce-a568108c308e" />

*The registration interface.*

<img width="1919" height="969" alt="Screenshot 2025-11-24 165025" src="https://github.com/user-attachments/assets/067588f3-a155-42c9-b47c-aeb70aab621f" />

*The login interface.*

<img width="1918" height="967" alt="Screenshot 2025-11-24 165046" src="https://github.com/user-attachments/assets/fe0ce8f9-82b2-4a8f-be0e-7500104cbc4a" />

*The goal management interface.*

<img width="1914" height="969" alt="Screenshot 2025-11-24 165220" src="https://github.com/user-attachments/assets/bdcd0d7b-78ff-43fb-8640-f96e81af4013" />

<img width="1919" height="909" alt="Screenshot 2025-11-24 165243" src="https://github.com/user-attachments/assets/f1dffe56-0bca-4ffe-8931-088bb1b6c0ec" />

*The subject management interface.*

<img width="1919" height="911" alt="Screenshot 2025-11-24 165331" src="https://github.com/user-attachments/assets/a3e39b90-2d3d-4233-94be-7facb8955e3e" />


*The report management interface.*

<img width="1919" height="911" alt="Screenshot 2025-11-24 165345" src="https://github.com/user-attachments/assets/c8156693-1e87-4e43-a54b-d75e3817831d" />

*The badges management interface.*

<img width="1919" height="911" alt="Screenshot 2025-11-24 165357" src="https://github.com/user-attachments/assets/5a61f09f-7ade-4c77-a966-18ee044d829c" />

*The timer interface.*

<img width="1919" height="907" alt="Screenshot 2025-11-24 165416" src="https://github.com/user-attachments/assets/18630de7-2949-4775-922a-351209d84ab5" />

*The To-Do management interface.*

<img width="1919" height="910" alt="Screenshot 2025-11-24 165636" src="https://github.com/user-attachments/assets/149f7725-9b7f-447c-9c60-fb50bf1d70c8" />

*The profile management interface.*

<img width="1919" height="911" alt="Screenshot 2025-11-24 165701" src="https://github.com/user-attachments/assets/af94c936-6851-4a11-bc20-c39c697b25d4" />

<img width="1919" height="910" alt="Screenshot 2025-11-24 165730" src="https://github.com/user-attachments/assets/82e64516-a422-4cb6-ad05-8a379e5c1549" />
```
```
