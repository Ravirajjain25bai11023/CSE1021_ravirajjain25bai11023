CREATE DATABASE IF NOT EXISTS student_tracker_db;
USE student_tracker_db;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    last_login DATETIME NOT NULL,
    study_streak INT DEFAULT 0,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Goals Table
CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    target_score DECIMAL(10, 2) NOT NULL,
    current_progress INT DEFAULT 0,
    status ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending',
    deadline DATE NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_deadline (deadline)
);

-- Subjects Table
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    UNIQUE KEY unique_user_subject (user_id, subject_name)
);

-- Progress Logs Table
CREATE TABLE progress_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT NULL,
    subject_id INT NOT NULL,
    marks_scored DECIMAL(10, 2) NOT NULL,
    date_logged DATETIME NOT NULL,
    notes TEXT,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX idx_goal_id (goal_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_date_logged (date_logged)
);

-- Study Sessions Table
CREATE TABLE study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_id INT NOT NULL,
    duration_minutes INT NOT NULL,
    session_date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_session_date (session_date)
);

-- Badges Table
CREATE TABLE badges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    badge_type ENUM('streak', 'achievement', 'special') NOT NULL,
    earned_date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    UNIQUE KEY unique_user_badge (user_id, badge_name)
);

-- Activity Logs Table
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_activity_type (activity_type)
);

-- Todo Tasks Table
CREATE TABLE todo_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed)
);

-- Insert sample motivational messages (for future use)
CREATE TABLE motivation_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    category VARCHAR(50) NOT NULL
);

-- Sample motivational data
INSERT INTO motivation_messages (message, category) VALUES
('Keep going! Every small step counts towards your big goal.', 'encouragement'),
('You are capable of amazing things. Believe in yourself!', 'confidence'),
('Success is the sum of small efforts repeated day in and day out.', 'persistence'),
('The expert in anything was once a beginner.', 'growth'),
('Your hard work will pay off. Stay focused!', 'motivation'),
('Progress, not perfection. You are doing great!', 'encouragement'),
('Dream big, work hard, stay focused!', 'motivation'),
('Every accomplishment starts with the decision to try.', 'inspiration'),
('You are stronger than you think!', 'confidence'),
('Consistency is the key to success. Keep it up!', 'persistence');
