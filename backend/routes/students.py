from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from backend.database import get_db_dataframe
from analysis.attendance_calculator import calculate_overall
from analysis.trend_analysis import analyze_trend
from analysis.absence_detection import detect_absence_patterns
from risk_ai.risk_engine import classify_risk

router = APIRouter(tags=["Students"])

@router.get("/students")
@router.get("/api/students")
def get_all_students(
    department: Optional[str] = Query(None, description="Filter by department (e.g., CSE)"),
    year: Optional[int] = Query(None, description="Filter by academic year (e.g., 2)"),
    section: Optional[str] = Query(None, description="Filter by section (e.g., A)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Low, Moderate, High)")
):
    """
    Get list of all students with overall attendance percentage and risk level.
    """
    df = get_db_dataframe()
    if df.empty:
        return []

    # Get unique students
    student_cols = ['student_id', 'student_name', 'department', 'year', 'section']
    available_cols = [c for c in student_cols if c in df.columns]
    
    unique_students_df = df[available_cols].drop_duplicates(subset=['student_id'])
    
    students_list = []
    for _, row in unique_students_df.iterrows():
        sid = str(row['student_id'])
        dept = str(row.get('department', ''))
        yr = int(row.get('year', 1))
        sec = str(row.get('section', ''))
        name = str(row.get('student_name', ''))

        # Apply basic filters
        if department and dept.lower() != department.lower():
            continue
        if year and yr != year:
            continue
        if section and sec.lower() != section.lower():
            continue

        pct = calculate_overall(sid, df)
        trend_info = analyze_trend(sid, df)
        absence_info = detect_absence_patterns(sid, df)
        risk = classify_risk(pct, trend_info['trend_label'], absence_info['max_consecutive_absences'], len(absence_info['weak_subjects']))

        if risk_level and risk.lower() != risk_level.lower():
            continue

        students_list.append({
            "student_id": sid,
            "student_name": name,
            "department": dept,
            "year": yr,
            "section": sec,
            "overall_attendance_pct": pct,
            "risk_level": risk,
            "trend_label": trend_info['trend_label']
        })

    return students_list

@router.get("/student/{student_id}")
@router.get("/api/student/{student_id}")
@router.get("/api/students/{student_id}")
def get_student_detail(student_id: str):
    """
    Get detailed profile for a specific student.
    """
    df = get_db_dataframe()
    student_df = df[df['student_id'] == student_id]
    if student_df.empty:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found.")

    first_row = student_df.iloc[0]
    pct = calculate_overall(student_id, df)
    trend_info = analyze_trend(student_id, df)
    absence_info = detect_absence_patterns(student_id, df)
    risk = classify_risk(pct, trend_info['trend_label'], absence_info['max_consecutive_absences'], len(absence_info['weak_subjects']))

    return {
        "student_id": str(first_row['student_id']),
        "student_name": str(first_row['student_name']),
        "department": str(first_row['department']),
        "year": int(first_row['year']),
        "section": str(first_row['section']),
        "overall_attendance_pct": pct,
        "risk_level": risk,
        "trend_label": trend_info['trend_label'],
        "total_records": len(student_df)
    }
