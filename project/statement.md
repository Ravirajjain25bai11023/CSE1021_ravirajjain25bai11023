# Project Statement

## 1. Problem Statement
**Why this project exists:**

Most students struggle to keep their academic life organized, but the current tools available are either too simple or too complicated.

We usually end up with a fragmented system: an Excel sheet for calculating grades, sticky notes for deadlines, a random mobile app for a focus timer, and a mental checklist for goals. There is no central "command center" where a student can see their academic health at a glance.

This lack of organization leads to missed deadlines, vague goals ("I want to do better"), and a lack of motivation because progress isn't visualized clearly. I built the **Student Academic Goal & Progress Tracker** to solve this fragmentation by bringing goals, grades, analytics, and productivity tools into one self-hosted dashboard.

---

## 2. Scope of the Project
This application is designed to be a personal academic assistant. It is **not** a Learning Management System (LMS) for teachers to grade students; rather, it is a tool for students to grade themselves and take ownership of their progress.

**The project covers:**
* **Data Aggregation:** collecting grades, study hours, and goal metrics in one database.
* **Visualization:** Converting raw data into meaningful charts (using Matplotlib) to show trends over time.
* **Habit Building:** Using gamification (badges/streaks) to encourage consistent study habits.
* **Privacy:** A self-contained, locally hosted environment where user data is not shared with third parties.

**Out of Scope:**
* Collaboration tools (group chats/forums).
* Teacher interfaces or assignment submissions.
* Mobile native apps (this is strictly a web application).

---

## 3. Target Users
Who is this built for?

* **University & High School Students:** Those who have multiple subjects to juggle and need to track distinct grading criteria.
* **Self-Learners:** Individuals taking online courses who need a way to structure their own learning path without an external institution.
* **Data-Driven Students:** People who get motivated by seeing their progress bars go up and want analytics on their performance.

---

## 4. High-Level Features
The system is built around four main pillars:

* **Academic Tracking:**
    * **Goal Setting:** Define clear targets (e.g., "Get an A in Calculus") with deadlines.
    * **Subject Logs:** Record marks and test scores to calculate running averages.
* **Visual Analytics:**
    * **Dashboard:** A visual overview featuring pie charts for goal completion and line graphs for weekly progress.
    * **Performance Metrics:** Automatic calculation of success rates and study consistency.
* **Productivity Tools:**
    * **Pomodoro Timer:** A built-in focus timer to manage study sessions without leaving the app.
    * **To-Do List:** specific daily task management integrated into the dashboard.
* **Gamification & Motivation:**
    * **Badge System:** visual rewards for consistent logins, high scores, and meeting deadlines.
    * **Streak Counter:** A daily counter to encourage everyday usage.
