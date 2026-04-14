DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS certificates;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
DROP VIEW IF EXISTS event_analytics;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    venue TEXT,
    event_date TEXT NOT NULL,
    event_time TEXT NOT NULL,
    registration_deadline TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    organizer_id INTEGER NOT NULL,
    banner_url TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    min_team_size INTEGER DEFAULT 1,
    max_team_size INTEGER DEFAULT 1,
    status TEXT DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_name TEXT NOT NULL,
    participant_email TEXT NOT NULL,
    team_name TEXT,
    team_members TEXT,
    event_id INTEGER NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attendance_status TEXT DEFAULT 'registered',
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(participant_email, event_id)
);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(registration_id, event_id)
);

CREATE TABLE certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(registration_id, event_id, type)
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_id INTEGER,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL
);

INSERT INTO users (name, email, password_hash, role) VALUES 
('System Admin', 'admin@college.edu', '$2b$12$xG1QkLwzR06O6Vq/vN/yUOSKzj9I39eCWeEHKO.p01E5U6T.O830a', 'admin');

INSERT INTO users (name, email, password_hash, role, department) VALUES 
('Alice Organizer', 'alice@college.edu', '$2b$12$xG1QkLwzR06O6Vq/vN/yUOSKzj9I39eCWeEHKO.p01E5U6T.O830a', 'organizer', 'Computer Science'),
('Bob Organizer', 'bob@college.edu', '$2b$12$xG1QkLwzR06O6Vq/vN/yUOSKzj9I39eCWeEHKO.p01E5U6T.O830a', 'organizer', 'Mechanical');



INSERT INTO events (title, description, category, venue, event_date, event_time, registration_deadline, capacity, organizer_id) VALUES 
('Tech Symposium 2024', 'Annual tech fest with coding and robotics.', 'technical', 'Main Auditorium', '2025-10-15', '09:00', '2025-10-10 23:59', 200, 2),
('Cultural Night', 'Dance, music and more.', 'cultural', 'Open Air Theatre', '2025-11-20', '18:00', '2025-11-15 23:59', 500, 3),
('AI Workshop', 'Hands-on AI and ML workshop.', 'workshop', 'Lab 4', '2024-05-10', '10:00', '2024-05-08 23:59', 30, 2),
('Inter-college Football', 'Football tournament.', 'sports', 'Main Ground', '2025-09-01', '16:00', '2025-08-25 23:59', 100, 3);

-- ==========================================
-- ADVANCED DBMS FEATURES
-- ==========================================

-- 1. AUDIT LOGS TABLE
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. DATABASE TRIGGERS
CREATE TRIGGER after_event_insert
AFTER INSERT ON events
BEGIN
    INSERT INTO audit_logs (table_name, action, record_id) VALUES ('events', 'INSERT', NEW.id);
END;

CREATE TRIGGER after_event_update
AFTER UPDATE ON events
BEGIN
    INSERT INTO audit_logs (table_name, action, record_id) VALUES ('events', 'UPDATE', NEW.id);
END;

CREATE TRIGGER after_event_delete
AFTER DELETE ON events
BEGIN
    INSERT INTO audit_logs (table_name, action, record_id) VALUES ('events', 'DELETE', OLD.id);
END;

-- 3. VIEWS (Complex Aggregation)
CREATE VIEW event_analytics AS
SELECT 
    e.id AS event_id,
    e.title,
    e.category,
    e.capacity,
    u.name AS organizer_name,
    COUNT(r.id) AS total_registrations,
    SUM(CASE WHEN r.attendance_status = 'attended' THEN 1 ELSE 0 END) AS total_attended,
    SUM(CASE WHEN r.attendance_status = 'waitlisted' THEN 1 ELSE 0 END) AS total_waitlisted,
    AVG(f.rating) AS average_rating
FROM events e
LEFT JOIN users u ON e.organizer_id = u.id
LEFT JOIN registrations r ON e.id = r.event_id
LEFT JOIN feedback f ON e.id = f.event_id
GROUP BY e.id;

-- 4. INDICES
CREATE INDEX idx_event_date ON events(event_date);
CREATE INDEX idx_registration_status ON registrations(attendance_status);
CREATE INDEX idx_event_category ON events(category);
