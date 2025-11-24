CREATE DATABASE IF NOT EXISTS student_tracker_db;
USE student_tracker_db;

-- Users table
CREATE TABLE users (
    uid             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    pwd_hash        VARCHAR(255) NOT NULL,
    joined_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME,
    streak          INT DEFAULT 0,
    
    UNIQUE KEY (username)
) ENGINE=InnoDB;

-- Subjects (lookup table)
CREATE TABLE subjects (
    sid             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    name            VARCHAR(64) NOT NULL,
    added_on        DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    UNIQUE KEY uk_user_sub (uid, name)
) ENGINE=InnoDB;

-- Core goals
-- added check constraint to stop invalid percentages
CREATE TABLE goals (
    gid             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    subject         VARCHAR(100) NOT NULL,
    target_score    DECIMAL(5,2) NOT NULL CHECK (target_score <= 100),
    progress        INT UNSIGNED DEFAULT 0 CHECK (progress <= 100),
    status          ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending',
    due_date        DATE NOT NULL,
    description     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    -- Composite index for the dashboard "upcoming" query
    INDEX idx_dashboard (uid, status, due_date)
) ENGINE=InnoDB;

-- Tracking logs
-- NOTE: Removed cascade delete here so we keep history even if goal is deleted
CREATE TABLE progress_logs (
    log_id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    gid             INT UNSIGNED,
    sid             INT UNSIGNED NOT NULL,
    marks           DECIMAL(5,2),
    logged_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes           TEXT,

    FOREIGN KEY (gid) REFERENCES goals(gid) ON DELETE SET NULL,
    FOREIGN KEY (sid) REFERENCES subjects(sid),
    INDEX idx_recent (sid, logged_at) 
) ENGINE=InnoDB;

-- Timer sessions
CREATE TABLE study_sessions (
    sess_id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    sid             INT UNSIGNED NOT NULL,
    duration_mins   INT UNSIGNED NOT NULL CHECK (duration_mins > 0), 
    sess_date       DATETIME NOT NULL,

    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (sid) REFERENCES subjects(sid),
    -- helps calc total study time per subject
    INDEX idx_analytics (uid, sid, duration_mins)
) ENGINE=InnoDB;

-- Badge system
CREATE TABLE badges (
    bid             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    badge_name      VARCHAR(100) NOT NULL,
    type            ENUM('streak', 'achievement', 'special') NOT NULL,
    earned_on       DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    UNIQUE KEY uk_one_badge (uid, badge_name)
) ENGINE=InnoDB;

-- Audit trail / Activity
CREATE TABLE activity_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    act_type        VARCHAR(32) NOT NULL,
    details         TEXT,
    ts              DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    INDEX idx_timeline (uid, ts DESC)
) ENGINE=InnoDB;

-- Simple Todo
CREATE TABLE todo_tasks (
    tid             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uid             INT UNSIGNED NOT NULL,
    task            VARCHAR(255) NOT NULL,
    is_done         TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
    INDEX idx_pending (uid, is_done)
) ENGINE=InnoDB;

-- Static data for motivation widget
CREATE TABLE motivation_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    msg TEXT NOT NULL,
    cat VARCHAR(32) DEFAULT 'general'
);

-- Initial seed
INSERT INTO motivation_messages (msg, cat) VALUES 
('Keep going! Every small step counts.', 'encouragement'),
('You are capable of amazing things.', 'confidence'),
('Success is the sum of small efforts.', 'persistence'),
('The expert in anything was once a beginner.', 'growth'),
('Stay focused!', 'motivation'),
('Progress, not perfection.', 'encouragement'),
('Dream big, work hard.', 'motivation'),
('You are stronger than you think!', 'confidence'),
('Consistency is key.', 'persistence');
