"""
Member 13 - Testing
Integration tests for the FastAPI backend (Member 10):
/health, /students, /student/{id}, /attendance/{id}, /risk/{id}

Run with:
    pytest tests/test_apis.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_student_id():
    """Pull a real student ID from the live dataset for the other tests to reuse."""
    resp = client.get("/students")
    assert resp.status_code == 200
    students = resp.json()
    assert len(students) > 0
    return students[0]["student_id"]


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------
def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert "endpoints" in body


# ---------------------------------------------------------------------------
# /students
# ---------------------------------------------------------------------------
def test_get_all_students():
    resp = client.get("/students")
    assert resp.status_code == 200
    students = resp.json()
    assert isinstance(students, list)
    assert len(students) > 0
    first = students[0]
    for key in ("student_id", "student_name", "overall_attendance_pct", "risk_level"):
        assert key in first


def test_get_students_filtered_by_risk_level():
    resp = client.get("/students", params={"risk_level": "High"})
    assert resp.status_code == 200
    students = resp.json()
    assert all(s["risk_level"] == "High" for s in students)


def test_get_students_filtered_by_department():
    resp = client.get("/students", params={"department": "CSE"})
    assert resp.status_code == 200
    students = resp.json()
    assert all(s["department"].lower() == "cse" for s in students)


# ---------------------------------------------------------------------------
# /student/{id}
# ---------------------------------------------------------------------------
def test_get_student_detail(sample_student_id):
    resp = client.get(f"/student/{sample_student_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["student_id"] == sample_student_id
    assert "risk_level" in body
    assert "trend_label" in body


def test_get_student_detail_not_found():
    resp = client.get("/student/DOES_NOT_EXIST")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# /attendance/{id}
# ---------------------------------------------------------------------------
def test_get_attendance_summary(sample_student_id):
    resp = client.get(f"/attendance/{sample_student_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["student_id"] == sample_student_id
    assert isinstance(body["subject_wise"], list)
    assert isinstance(body["weekly_trend"], list)
    assert isinstance(body["monthly_trend"], list)


def test_get_attendance_not_found():
    resp = client.get("/attendance/DOES_NOT_EXIST")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# /risk/{id}
# ---------------------------------------------------------------------------
def test_get_risk_and_insight(sample_student_id):
    resp = client.get(f"/risk/{sample_student_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] in ("Low", "Moderate", "High")
    assert isinstance(body["ai_insight"], str)
    assert len(body["ai_insight"]) > 0


def test_get_risk_not_found():
    resp = client.get("/risk/DOES_NOT_EXIST")
    assert resp.status_code == 404
