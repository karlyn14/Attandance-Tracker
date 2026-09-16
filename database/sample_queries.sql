-- ================================================================
-- AI-Based Student Attendance Monitoring & Early-Warning System
-- FILE   : database/sample_queries.sql
-- Member : 2 — Database Developer
-- Run AFTER import_csv.py has loaded data into the DB
-- Present + Late + On Duty all count as "attended"
-- ================================================================


-- ----------------------------------------------------------------
-- QUERY 1: Overall Attendance % Per Student
-- Sorted worst-first so highest-risk students appear at top.
-- ----------------------------------------------------------------
SELECT
    s.student_id,
    s.name,
    s.department,
    s.year,
    s.section,
    COUNT(a.attendance_id)                                        AS total_classes,
    SUM(a.status IN ('Present','Late','On Duty'))                 AS attended,
    SUM(a.status = 'Absent')                                      AS absences,
    ROUND(
        SUM(a.status IN ('Present','Late','On Duty'))
        / COUNT(a.attendance_id) * 100, 2
    )                                                             AS attendance_pct
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.name, s.department, s.year, s.section
ORDER BY attendance_pct ASC;


-- ----------------------------------------------------------------
-- QUERY 2: Absences Per Student Per Subject
-- Shows which subject each student skips the most.
-- ----------------------------------------------------------------
SELECT
    s.student_id,
    s.name,
    sub.subject_name,
    COUNT(a.attendance_id)                                        AS total_classes,
    SUM(a.status = 'Absent')                                      AS absences,
    ROUND(
        SUM(a.status = 'Absent') / COUNT(a.attendance_id) * 100, 2
    )                                                             AS absence_pct
FROM Students s
JOIN Attendance a   ON s.student_id = a.student_id
JOIN Subjects   sub ON a.subject_id = sub.subject_id
GROUP BY s.student_id, s.name, sub.subject_name
ORDER BY s.student_id, absence_pct DESC;


-- ----------------------------------------------------------------
-- QUERY 3: Students Below 75% — At-Risk List
-- Core feed for the early-warning system.
-- Includes computed risk band: High (<60%), Medium (60-74%).
-- ----------------------------------------------------------------
SELECT
    s.student_id,
    s.name,
    s.department,
    s.year,
    s.section,
    ROUND(
        SUM(a.status IN ('Present','Late','On Duty'))
        / COUNT(a.attendance_id) * 100, 2
    )                                                             AS attendance_pct,
    CASE
        WHEN SUM(a.status IN ('Present','Late','On Duty'))
             / COUNT(a.attendance_id) * 100 < 60  THEN 'High'
        ELSE 'Medium'
    END                                                           AS risk_level
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.name, s.department, s.year, s.section
HAVING attendance_pct < 75
ORDER BY attendance_pct ASC;


-- ----------------------------------------------------------------
-- QUERY 4: Monthly Attendance Trend Per Student
-- Detects students whose attendance is declining month-by-month.
-- ----------------------------------------------------------------
SELECT
    s.student_id,
    s.name,
    DATE_FORMAT(a.att_date, '%Y-%m')                              AS month,
    COUNT(a.attendance_id)                                        AS total_classes,
    SUM(a.status IN ('Present','Late','On Duty'))                 AS attended,
    ROUND(
        SUM(a.status IN ('Present','Late','On Duty'))
        / COUNT(a.attendance_id) * 100, 2
    )                                                             AS monthly_pct
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.name, month
ORDER BY s.student_id, month;


-- ----------------------------------------------------------------
-- QUERY 5: Risk Level Dashboard Summary
-- One-line count of High / Medium / Low risk students.
-- Designed for Member 11-12's dashboard summary card.
-- Needs Risk table populated (done by import_csv.py).
-- ----------------------------------------------------------------
SELECT
    r.risk_level,
    COUNT(r.student_id)                                           AS student_count
FROM Risk r
GROUP BY r.risk_level
ORDER BY FIELD(r.risk_level, 'High', 'Medium', 'Low');


-- ----------------------------------------------------------------
-- QUERY 6: Department-wise Attendance Summary (Admin / HOD view)
-- ----------------------------------------------------------------
SELECT
    s.department,
    COUNT(DISTINCT s.student_id)                                  AS total_students,
    ROUND(
        SUM(a.status IN ('Present','Late','On Duty'))
        / COUNT(a.attendance_id) * 100, 2
    )                                                             AS dept_attendance_pct
FROM Students s
JOIN Attendance a ON s.student_id = a.student_id
GROUP BY s.department
ORDER BY dept_attendance_pct ASC;
