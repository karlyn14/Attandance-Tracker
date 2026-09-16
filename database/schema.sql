USE attendance_db;
DROP TABLE IF EXISTS Risk;
DROP TABLE IF EXISTS Attendance;
DROP TABLE IF EXISTS Subjects;
DROP TABLE IF EXISTS Students;

-- ----------------------------------------------------------------
-- TABLE 1: Students
-- ----------------------------------------------------------------
CREATE TABLE Students (
    student_id   VARCHAR(20)  NOT NULL,           -- e.g. STU0001
    name         VARCHAR(100) NOT NULL,
    department   VARCHAR(50)  NOT NULL,            -- IT,CSE,ECE,MECH,EEE,CIVIL
    year         TINYINT      NOT NULL
                 CHECK (year BETWEEN 1 AND 4),
    section      CHAR(1)      NOT NULL,            -- A, B, C
    PRIMARY KEY (student_id)
);

-- ----------------------------------------------------------------
-- TABLE 2: Subjects
-- ----------------------------------------------------------------
CREATE TABLE Subjects (
    subject_id   VARCHAR(10)  NOT NULL,            -- e.g. SUB001
    subject_name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (subject_id)
);

-- ----------------------------------------------------------------
-- TABLE 3: Attendance
-- One row per student × subject × date × period
-- ----------------------------------------------------------------
CREATE TABLE Attendance (
    attendance_id INT          NOT NULL AUTO_INCREMENT,
    student_id    VARCHAR(20)  NOT NULL,
    subject_id    VARCHAR(10)  NOT NULL,
    att_date      DATE         NOT NULL,
    period        TINYINT      NOT NULL
                  CHECK (period BETWEEN 1 AND 8),
    status        ENUM('Present','Absent','Late','On Duty','Unknown')
                               NOT NULL DEFAULT 'Absent',
    PRIMARY KEY (attendance_id),
    UNIQUE KEY uq_att (student_id, subject_id, att_date, period),
    CONSTRAINT fk_att_student FOREIGN KEY (student_id)
        REFERENCES Students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_att_subject FOREIGN KEY (subject_id)
        REFERENCES Subjects(subject_id)  ON DELETE RESTRICT
);

-- ----------------------------------------------------------------
-- TABLE 4: Risk
-- One row per student — updated after each ML / analysis run
-- Backend (Member 10) calls: INSERT ... ON DUPLICATE KEY UPDATE
-- ----------------------------------------------------------------
CREATE TABLE Risk (
    student_id  VARCHAR(20)  NOT NULL,
    risk_level  ENUM('Low','Medium','High') NOT NULL DEFAULT 'Low',
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id),
    CONSTRAINT fk_risk_student FOREIGN KEY (student_id)
        REFERENCES Students(student_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------
-- INDEXES — speeds up every query below
-- ----------------------------------------------------------------
CREATE INDEX idx_att_student_date ON Attendance (student_id, att_date);
CREATE INDEX idx_att_subject       ON Attendance (subject_id);
CREATE INDEX idx_att_status        ON Attendance (status);
CREATE INDEX idx_risk_level        ON Risk       (risk_level);
