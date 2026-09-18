"""
Members 11-12 - Dashboard data layer.
Bridges the raw dataset + analysis/risk_ai modules into the shapes
dashboard/app.py and its components expect.
"""

import os
import sys

_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_DASHBOARD_DIR)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

import pandas as pd

from analysis.attendance_calculator import calculate_overall
from analysis.trend_analysis import analyze_trend
from analysis.absence_detection import detect_absence_patterns
from risk_ai.risk_engine import classify_risk

_RAW_CSV_PATH = os.path.join(_BASE_DIR, "data", "attendance.csv")


def _load_raw() -> pd.DataFrame:
    df = pd.read_csv(_RAW_CSV_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date", "student_id"])


def get_student_timeline(raw_df: pd.DataFrame, student_id: str) -> pd.DataFrame:
    """Per-day attendance % for one student — feeds the timeline chart."""
    student_df = raw_df[raw_df["student_id"] == student_id].copy()
    if student_df.empty:
        return pd.DataFrame(columns=["date", "pct"])
    student_df["is_present"] = student_df["status"].str.lower().eq("present")
    daily = student_df.groupby("date")["is_present"].agg(["sum", "count"]).reset_index()
    daily["pct"] = daily["sum"] / daily["count"] * 100
    return daily[["date", "pct"]].sort_values("date")


def get_student_subjects(raw_df: pd.DataFrame, student_id: str) -> pd.DataFrame:
    """Subject-wise present/late/absent breakdown for one student."""
    student_df = raw_df[raw_df["student_id"] == student_id]
    cols = ["subject", "total_classes", "presents", "lates", "absents", "attendance_rate"]
    if student_df.empty:
        return pd.DataFrame(columns=cols)

    rows = []
    for subject, g in student_df.groupby("subject"):
        total = len(g)
        presents = int((g["status"].str.lower() == "present").sum())
        lates = int((g["status"].str.lower() == "late").sum())
        absents = int((g["status"].str.lower() == "absent").sum())
        rows.append({
            "subject": subject,
            "total_classes": total,
            "presents": presents,
            "lates": lates,
            "absents": absents,
            "attendance_rate": presents / total * 100 if total else 0.0,
        })
    return pd.DataFrame(rows, columns=cols).sort_values("attendance_rate")


def load_dataset():
    """
    Returns:
      students - one row per student with attendance/risk summary
      raw_df   - full raw attendance log (all statuses kept, for the list view)
      trend    - cohort-wide daily attendance % (for the overview chart)
    """
    raw_df = _load_raw()

    rows = []
    for sid in raw_df["student_id"].drop_duplicates():
        student_records = raw_df[raw_df["student_id"] == sid]
        first = student_records.iloc[0]

        overall_pct = calculate_overall(sid, raw_df)
        trend_info = analyze_trend(sid, raw_df)
        absence_info = detect_absence_patterns(sid, raw_df)
        risk = classify_risk(
            overall_pct,
            trend_info["trend_label"],
            absence_info["max_consecutive_absences"],
            len(absence_info["weak_subjects"]),
        )

        rows.append({
            "student_id": sid,
            "name": first["student_name"],
            "department": first["department"],
            "year": first["year"],
            "section": first["section"],
            "attendance_rate": overall_pct,
            "total_sessions": len(student_records),
            "recent_absences": int((student_records["status"].str.lower() == "absent").sum()),
            "lates": int((student_records["status"].str.lower() == "late").sum()),
            # NOTE: placeholder — no real GPA column exists in the dataset yet.
            "gpa": round(6.0 + (overall_pct / 100) * 4.0, 2),
            "risk_level": risk,
        })

    students = pd.DataFrame(rows)

    raw_df = raw_df.copy()
    raw_df["is_present"] = raw_df["status"].str.lower().eq("present")
    daily = raw_df.groupby("date")["is_present"].agg(["sum", "count"]).reset_index()
    daily["pct"] = daily["sum"] / daily["count"] * 100
    trend = daily[["date", "pct"]].sort_values("date")

    return students, raw_df, trend
