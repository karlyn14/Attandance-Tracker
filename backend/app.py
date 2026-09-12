from flask import Flask
from flask_cors import CORS
from routes.students import students_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(students_bp)


attendance = {
    "S101": {
        "attendance": 82,
        "present_classes": 41,
        "total_classes": 50
    },
    "S102": {
        "attendance": 94,
        "present_classes": 47,
        "total_classes": 50
    },
    "S103": {
        "attendance": 73,
        "present_classes": 36,
        "total_classes": 50
    }
}
risk_data = {
    "S101": {
        "risk": "Moderate",
        "trend": "stable",
        "insight": "Attendance is moderate and should be monitored."
    },
    "S102": {
        "risk": "Low",
        "trend": "increasing",
        "insight": "Attendance is good and showing a positive trend."
    },
    "S103": {
        "risk": "High",
        "trend": "decreasing",
        "insight": "Attendance is declining and requires attention."
    }
}


@app.route("/")
def home():
    return {
        "message": "Attendance Monitoring Backend is running"
    }


@app.route("/attendance/<student_id>")
def get_attendance(student_id):

    if student_id in attendance:
        return {
            "student_id": student_id,
            **attendance[student_id]
        }

    return {
        "error": "Attendance data not found"
    }, 404

@app.route("/risk/<student_id>")
def get_risk(student_id):

    if student_id in risk_data:
        return {
            "student_id": student_id,
            **risk_data[student_id]
        }

    return {
        "error": "Risk data not found"
    }, 404


if __name__ == "__main__":
    app.run(debug=True)

