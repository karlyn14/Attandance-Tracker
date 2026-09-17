from fastapi import APIRouter, HTTPException
from backend.database import get_db_dataframe
from analysis.attendance_calculator import calculate_overall
from analysis.trend_analysis import analyze_trend
from analysis.absence_detection import detect_absence_patterns
from risk_ai.risk_engine import classify_risk
from risk_ai.insight_generator import generate_insight

router = APIRouter(tags=["Risk & AI Insights"])

@router.get("/risk/{student_id}")
@router.get("/api/risk/{student_id}")
def get_risk_and_insight(student_id: str):
    """
    Get risk assessment metrics and AI-generated insight text for a student.
    """
    df = get_db_dataframe()
    student_df = df[df['student_id'] == student_id]
    if student_df.empty:
        raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found for risk evaluation.")

    student_name = str(student_df.iloc[0]['student_name'])
    overall_pct = calculate_overall(student_id, df)
    trend_info = analyze_trend(student_id, df)
    absence_info = detect_absence_patterns(student_id, df)

    risk_level = classify_risk(
        overall_pct=overall_pct,
        trend_label=trend_info['trend_label'],
        consecutive_absences=absence_info['max_consecutive_absences'],
        weak_subjects_count=len(absence_info['weak_subjects'])
    )

    ai_insight = generate_insight(
        student_name=student_name,
        overall_pct=overall_pct,
        trend_label=trend_info['trend_label'],
        consecutive_absences=absence_info['max_consecutive_absences'],
        weak_subjects=absence_info['weak_subjects'],
        risk_level=risk_level
    )

    return {
        "student_id": student_id,
        "student_name": student_name,
        "overall_pct": overall_pct,
        "risk_level": risk_level,
        "trend_label": trend_info['trend_label'],
        "max_consecutive_absences": absence_info['max_consecutive_absences'],
        "frequent_day_absent": absence_info['frequent_day_absent'],
        "weak_subjects": absence_info['weak_subjects'],
        "ai_insight": ai_insight
    }
