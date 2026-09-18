"""
Member 13 - Testing
Unit tests for the calculation and analysis layer (Members 4-9):
attendance_calculator, trend_analysis, absence_detection, risk_engine,
insight_generator.

Run with:
    pytest tests/test_calculations.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytest

from analysis.attendance_calculator import calculate_overall, calculate_subject_wise
from analysis.trend_analysis import classify_trend, analyze_trend
from analysis.absence_detection import _max_consecutive_absences, detect_absence_patterns
from risk_ai.risk_engine import classify_risk
from risk_ai.insight_generator import generate_insight


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_df():
    """A small hand-built attendance dataframe with a known, predictable shape."""
    rows = [
        # S001: 3 present, 1 absent -> 75% overall, all in Math
        ("S001", "Test One", "CSE", 1, "A", "Math", "2026-01-05", 1, "Present"),
        ("S001", "Test One", "CSE", 1, "A", "Math", "2026-01-06", 1, "Present"),
        ("S001", "Test One", "CSE", 1, "A", "Math", "2026-01-07", 1, "Absent"),
        ("S001", "Test One", "CSE", 1, "A", "Math", "2026-01-08", 1, "Present"),
        # S002: all present -> 100%
        ("S002", "Test Two", "CSE", 1, "A", "Science", "2026-01-05", 2, "Present"),
        ("S002", "Test Two", "CSE", 1, "A", "Science", "2026-01-06", 2, "Present"),
    ]
    df = pd.DataFrame(rows, columns=[
        "student_id", "student_name", "department", "year", "section",
        "subject", "date", "period", "status",
    ])
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------------------------
# attendance_calculator (Member 4)
# ---------------------------------------------------------------------------
def test_calculate_overall_basic(sample_df):
    assert calculate_overall("S001", sample_df) == pytest.approx(75.0)
    assert calculate_overall("S002", sample_df) == pytest.approx(100.0)


def test_calculate_overall_unknown_student_returns_zero(sample_df):
    assert calculate_overall("NOPE", sample_df) == 0.0


def test_calculate_subject_wise_shape(sample_df):
    result = calculate_subject_wise("S001", sample_df)
    assert "attendance_pct" in result.columns
    row = result[result["subject"] == "Math"].iloc[0]
    assert row["present_classes"] == 3
    assert row["total_classes"] == 4


# ---------------------------------------------------------------------------
# trend_analysis (Member 5)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("pcts,expected_label", [
    ([90.0, 80.0, 70.0, 60.0], "decreasing"),
    ([60.0, 68.0, 75.0, 82.0], "increasing"),
    ([92.0, 91.0, 93.0, 92.0], "stable"),
    ([95.0, 94.0, 70.0, 68.0], "sudden_change"),
])
def test_classify_trend_labels(pcts, expected_label):
    result = classify_trend(pcts)
    assert result["label"] == expected_label


def test_classify_trend_insufficient_data():
    result = classify_trend([80.0])
    assert result["label"] == "insufficient_data"


def test_analyze_trend_returns_trend_label_key(sample_df):
    result = analyze_trend("S001", sample_df)
    assert "trend_label" in result


# ---------------------------------------------------------------------------
# absence_detection (Member 6)
# ---------------------------------------------------------------------------
def test_max_consecutive_absences():
    assert _max_consecutive_absences(["Absent", "Absent", "Absent", "Present"]) == 3
    assert _max_consecutive_absences(["Present", "Present"]) == 0
    assert _max_consecutive_absences(["Absent", "Present", "Absent"]) == 1


def test_detect_absence_patterns_shape(sample_df):
    result = detect_absence_patterns("S001", sample_df)
    assert set(result.keys()) == {"max_consecutive_absences", "weak_subjects", "frequent_day_absent"}
    assert result["max_consecutive_absences"] == 1


def test_detect_absence_patterns_unknown_student(sample_df):
    result = detect_absence_patterns("NOPE", sample_df)
    assert result["max_consecutive_absences"] == 0
    assert result["weak_subjects"] == []


# ---------------------------------------------------------------------------
# risk_engine (Member 7)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("pct,trend,consec,expected", [
    (90, "stable", 0, "Low"),
    (86, "increasing", 1, "Low"),
    (80, "stable", 1, "Moderate"),
    (87, "decreasing", 1, "Moderate"),
    (73, "decreasing", 3, "High"),
    (60, "stable", 0, "High"),
    (90, "stable", 4, "High"),
])
def test_classify_risk_matches_spec(pct, trend, consec, expected):
    assert classify_risk(pct, trend, consec) == expected


def test_classify_risk_weak_subjects_escalates():
    # Two or more weak subjects should push a borderline case to High
    assert classify_risk(90, "stable", 0, weak_subjects_count=2) == "High"


# ---------------------------------------------------------------------------
# insight_generator (Member 9)
# ---------------------------------------------------------------------------
def test_generate_insight_mentions_risk_level():
    text = generate_insight("Test Student", 73.0, "decreasing", 3, ["Math"], "High")
    assert "Risk level: High" in text
    assert "Test Student" in text


def test_generate_insight_no_absences_no_weak_subjects():
    text = generate_insight("Test Student", 95.0, "stable", 0, [], "Low")
    assert "Risk level: Low" in text
    assert "consecutive absence" not in text
