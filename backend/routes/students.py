from flask import Blueprint

students_bp = Blueprint("students", __name__)


students = [
    {
        "student_id": "S101",
        "name": "Arjun Kumar",
        "department": "CSE",
        "year": 2,
        "section": "A"
    },
    {
        "student_id": "S102",
        "name": "Divya Rao",
        "department": "CSE",
        "year": 2,
        "section": "A"
    },
    {
        "student_id": "S103",
        "name": "Rahul Kumar",
        "department": "CSE",
        "year": 2,
        "section": "A"
    }
]


@students_bp.route("/students")
def get_students():
    return {
        "students": students
    }


@students_bp.route("/student/<student_id>")
def get_student(student_id):

    for student in students:
        if student["student_id"] == student_id:
            return student

    return {
        "error": "Student not found"
    }, 404
