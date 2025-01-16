-- database_schema.sql

-- Table for school setup details
CREATE TABLE IF NOT EXISTS schools (
    school_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    academic_year_start DATE NOT NULL,
    academic_year_end DATE NOT NULL,
    session_duration_minutes INTEGER NOT NULL,
    break_duration_minutes INTEGER NOT NULL
);



-- Table for subjects
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    description TEXT
);

-- Table for grades
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_name TEXT NOT NULL,
    division_count INTEGER NOT NULL
);


-- Table for student leadership roles
CREATE TABLE IF NOT EXISTS student_leadership (
    leadership_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    leadership_role TEXT NOT NULL, -- e.g., "Head Boy", "Head Girl", "House Captain", "Class Monitor"
    grade_id INTEGER,
    FOREIGN KEY (grade_id) REFERENCES grades(grade_id)
);

-- Table for holidays and non-teaching days
CREATE TABLE IF NOT EXISTS non_teaching_days (
    day_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    event_date DATE NOT NULL
);

-- Table for teacher availability
CREATE TABLE IF NOT EXISTS teacher_availability (
    availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0 for Sunday, 1 for Monday, ..., 6 for Saturday
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);
-- Add to database_schema.sql

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    grade_id INTEGER,
    FOREIGN KEY (grade_id) REFERENCES grades(grade_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT CHECK(role IN ('admin', 'teacher')),
    name TEXT NOT NULL,
    contact_info TEXT,
    subject_id INTEGER,  -- Foreign key to subject
    availability TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

 CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT,
    message TEXT,
    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT,
    entity_id INTEGER,
    feedback TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    teacher_id INTEGER NOT NULL,
    division INTEGER NOT NULL,
    FOREIGN KEY (grade_id) REFERENCES grades(grade_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
     FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

CREATE TABLE leave_requests (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK( status IN ('Pending', 'Approved', 'Declined') ),
    applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);