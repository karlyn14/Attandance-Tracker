"""
Module: trend_analysis
Analyzes weekly attendance trajectories and classifies student trends.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


def compute_weekly_attendance(
    df: pd.DataFrame,
    student_col: str = "student_id",
    date_col: str = "date",
    status_col: str = "present",
) -> pd.DataFrame:
    """
    Aggregates daily records into weekly attendance percentages per student.
    Expects status_col to be binary (1 for present, 0 for absent) or boolean.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    # Group by student and calendar week start (Monday)
    df["week"] = df[date_col].dt.to_period("W").apply(lambda r: r.start_time)

    weekly = (
        df.groupby([student_col, "week"])[status_col]
        .agg(total_days="count", days_present="sum")
        .reset_index()
    )
    weekly["attendance_pct"] = (weekly["days_present"] / weekly["total_days"]) * 100.0
    return weekly.sort_values([student_col, "week"])


def classify_trend(
    weekly_pcts: List[float],
    sudden_threshold: float = 15.0,
    slope_threshold: float = 2.5,
    stable_band: float = 5.0,
) -> Dict[str, Optional[float]]:
    """
    Classifies attendance trajectory using week-over-week deltas and linear slope.

    Parameters:
    - weekly_pcts: Ordered sequence of weekly attendance % (0-100).
    - sudden_threshold: Single-week shift triggering 'sudden_change'.
    - slope_threshold: % per week change required to label increasing/decreasing.
    - stable_band: Max range (max - min) to qualify as 'stable' if slope is flat.

    Returns:
    - dict with keys: 'label', 'slope', 'max_single_week_change'
    """
    n = len(weekly_pcts)
    if n < 2:
        return {"label": "insufficient_data", "slope": None, "max_delta": None}

    series = np.array(weekly_pcts, dtype=float)
    deltas = np.diff(series)
    max_delta = float(np.max(np.abs(deltas)))

    # Compute linear slope (% change per week)
    x = np.arange(n)
    slope, _ = np.polyfit(x, series, deg=1)

    # Classification logic
    if max_delta >= sudden_threshold:
        label = "sudden_change"
    elif slope >= slope_threshold:
        label = "increasing"
    elif slope <= -slope_threshold:
        label = "decreasing"
    elif (np.max(series) - np.min(series)) <= stable_band:
        label = "stable"
    else:
        label = "fluctuating"

    return {
        "label": label,
        "slope": round(float(slope), 2),
        "max_delta": round(max_delta, 2),
    }


def analyze_student_trends(
    weekly_df: pd.DataFrame,
    student_col: str = "student_id",
    pct_col: str = "attendance_pct",
) -> pd.DataFrame:
    """
    Applies trend classification across all students in the weekly DataFrame.
    """
    records = []
    for student_id, group in weekly_df.groupby(student_col):
        pcts = group[pct_col].tolist()
        result = classify_trend(pcts)
        records.append({student_col: student_id, **result})
    return pd.DataFrame(records)


# ----------------------------------------------------------------------
# Day 1 Verification & Dummy Tests
# ----------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = {
        "Declining Student": [90.0, 80.0, 70.0, 60.0],
        "Increasing Student": [60.0, 68.0, 75.0, 82.0],
        "Stable Student": [92.0, 91.0, 93.0, 92.0],
        "Sudden Drop Student": [95.0, 94.0, 70.0, 68.0],
        "Fluctuating Student": [90.0, 78.0, 89.0, 77.0],
    }

    print(f"{'Case':<22} | {'Expected':<15} | {'Got':<15} | {'Slope':<7} | {'Status'}")
    print("-" * 75)

    expected = {
        "Declining Student": "decreasing",
        "Increasing Student": "increasing",
        "Stable Student": "stable",
        "Sudden Drop Student": "sudden_change",
        "Fluctuating Student": "fluctuating",
    }

    for name, seq in test_cases.items():
        res = classify_trend(seq)
        passed = res["label"] == expected[name]
        status = "PASS" if passed else "FAIL"
        print(
            f"{name:<22} | {expected[name]:<15} | {res['label']:<15} | {res['slope']:<7} | {status}"
        )
