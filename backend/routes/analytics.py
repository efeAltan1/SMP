from flask import Blueprint, jsonify
from models.subject import Subject
from models.grade import Grade
from models.attendance import Attendance
import numpy as np


bp = Blueprint('analytics', __name__)


# Get all analysis metrics. Create summaries of features like subject, grades, and attendance.
@bp.route('/summary', methods=['GET'])
def get_summary():
    subjects = Subject.find_all()
    grades = Grade.find_all()
    attendance = Attendance.find_all()

    total_subjects = len(subjects)
    total_grades = len(grades)
    total_attendance = len(attendance)
    present_count = sum(1 for r in attendance if r.data.get('status') == 'present')
    overall_attendance_rate = round((present_count / total_attendance) * 100, 2) if total_attendance > 0 else 0

    return jsonify({"status": "ok", "data": {
        "total_subjects": total_subjects,
        "total_grades": total_grades,
        "overall_attendance_rate": overall_attendance_rate
    }})


# Get analytics for grades. Calculate average, highest, lowest, and distribution of grades across all subjects.
@bp.route('/grades', methods=['GET'])
def get_grade_analytics():
    grades = Grade.find_all()
    if not grades:
        return jsonify({"status": "ok", "data": {}})

    scores = np.array([g.data['score'] for g in grades])
    weights = np.array([g.data['weight'] for g in grades])

    return jsonify({"status": "ok", "data": {
        "average": round(float(np.average(scores, weights=weights)), 2),
        "highest": float(np.max(scores)),
        "lowest": float(np.min(scores)),
        "distribution": {
            "90-100": int(np.sum(scores >= 90)),
            "80-89": int(np.sum((scores >= 80) & (scores < 90))),
            "70-79": int(np.sum((scores >= 70) & (scores < 80))),
            "60-69": int(np.sum((scores >= 60) & (scores < 70))),
            "below 60": int(np.sum(scores < 60))
        }
    }})


# Get analytics for subjects. Calculate average grade and attendance rate for each subject.
@bp.route('/subjects', methods=['GET'])
def get_subject_analytics():
    subjects = Subject.find_all()
    grades = Grade.find_all()
    attendance = Attendance.find_all()

    result = []
    for subject in subjects:
        sid = str(subject.data['_id'])

        subject_grades = [g for g in grades if g.data.get('subject_id') == sid]
        subject_attendance = [r for r in attendance if r.data.get('subject_id') == sid]

        avg_score = None
        if subject_grades:
            scores = np.array([g.data['score'] for g in subject_grades])
            weights = np.array([g.data['weight'] for g in subject_grades])
            avg_score = round(float(np.average(scores, weights=weights)), 2)

        attendance_rate = None
        if subject_attendance:
            total = len(subject_attendance)
            present = sum(1 for r in subject_attendance if r.data.get('status') == 'present')
            attendance_rate = round((present / total) * 100, 2)

        result.append({
            "subject": subject.to_dict(),
            "average_score": avg_score,
            "attendance_rate": attendance_rate
        })

    return jsonify({"status": "ok", "data": result})
