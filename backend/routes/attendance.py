from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.database import get_db_dataframe
from analysis.attendance_calculator import calculate_overall, calculate_subject_wise, calculate_weekly, calculate_monthly

router = APIRouter(tags=["Attendance"])

@router.get("/attendance/{student_id}")
@router.get("/api/attendance/{student_id}")
def get_attendance_summary(
    student_id: str,
    subject: Optional[str] = Query(None, description="Filter attendance by subject name"),
    start_date: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to end date (YYYY-MM-DD)")
):
    """
    Get detailed attendance calculations for a specific student,
    including subject-wise breakdown, weekly & monthly trends, and log records.
    """
    df = get_db_dataframe()
    student_df = df[df['student_id'] == student_id].copy()
    if student_df.empty:
        raise HTTPException(status_code=404, detail=f"No attendance records found for student ID '{student_id}'.")

    # Filter optional criteria
    if subject:
        student_df = student_df[student_df['subject'].str.lower() == subject.lower()]
    if start_date:
        student_df = student_df[student_df['date'] >= start_date]
    if end_date:
        student_df = student_df[student_df['date'] <= end_date]

    if student_df.empty:
        return {
            "student_id": student_id,
            "overall_pct": 0.0,
            "subject_wise": [],
            "weekly_trend": [],
            "monthly_trend": [],
            "records": []
        }

    overall_pct = calculate_overall(student_id, df)
    subject_wise = calculate_subject_wise(student_id, student_df)
    weekly_trend = calculate_weekly(student_id, student_df)
    monthly_trend = calculate_monthly(student_id, student_df)

    records = student_df[['subject', 'date', 'period', 'status']].to_dict(orient='records')

    return {
        "student_id": student_id,
        "overall_pct": overall_pct,
        "subject_wise": subject_wise,
        "weekly_trend": weekly_trend,
        "monthly_trend": monthly_trend,
        "total_classes": len(student_df),
        "records": records
    }
