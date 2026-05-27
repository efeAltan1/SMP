from flask import Blueprint, jsonify
from models.subject import Subject
from models.grade import Grade
from models.attendance import Attendance


bp = Blueprint('analytics', __name__)


LETTER_TO_GPA = {
    'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5,
    'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'FF': 0.0,
    'DZ': 0.0, 'G': 4.0
}


def parse_hours(value):
    try:
        return float(value.split()[0])
    except (ValueError, AttributeError, IndexError):
        return 0.0


# Summary card data for the dashboard: subject count, GPA, overall attendance rate.
@bp.route('/summary', methods=['GET'])
def get_summary():
    subjects = Subject.find_all()
    grades = Grade.find_all()
    attendance = Attendance.find_all()

    total_subjects = len(subjects)

    # GPA from letter grades + credits
    graded = [g for g in grades if g.data.get('letter_grade') in LETTER_TO_GPA]
    total_points = sum(LETTER_TO_GPA[g.data['letter_grade']] * (float(g.data.get('credits', 0) or 0)) for g in graded)
    total_credits = sum(float(g.data.get('credits', 0) or 0) for g in graded)
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    # Attendance rate: average across all courses
    rates = []
    for r in attendance:
        absence = parse_hours(r.data.get('theoretical_absence', '0'))
        max_hours = parse_hours(r.data.get('theoretical_max', '0'))
        if max_hours > 0:
            rates.append((1 - absence / max_hours) * 100)
    overall_attendance_rate = round(sum(rates) / len(rates), 2) if rates else 0.0

    return jsonify({"status": "ok", "data": {
        "total_subjects": total_subjects,
        "gpa": gpa,
        "overall_attendance_rate": overall_attendance_rate
    }})


# Per-subject breakdown: letter grade and attendance rate for each course.
@bp.route('/subjects', methods=['GET'])
def get_subject_analytics():
    subjects = Subject.find_all()
    grades = Grade.find_all()
    attendance = Attendance.find_all()

    # Build lookup dicts by course code
    grades_by_code = {}
    for g in grades:
        code = g.data.get('code')
        if code:
            grades_by_code.setdefault(code, []).append(g)

    attendance_by_code = {r.data.get('code'): r for r in attendance}

    result = []
    seen_codes = set()

    for subject in subjects:
        code = subject.data.get('code')
        if not code or code in seen_codes:
            continue
        seen_codes.add(code)

        subject_grades = grades_by_code.get(code, [])
        latest_grade = next((g for g in subject_grades if g.data.get('letter_grade')), None)
        letter_grade = latest_grade.data.get('letter_grade') if latest_grade else None

        attendance_record = attendance_by_code.get(code)
        attendance_rate = None
        if attendance_record:
            absence = parse_hours(attendance_record.data.get('theoretical_absence', '0'))
            max_hours = parse_hours(attendance_record.data.get('theoretical_max', '0'))
            if max_hours > 0:
                attendance_rate = round((1 - absence / max_hours) * 100, 2)

        result.append({
            "code": code,
            "name": subject.data.get('name'),
            "letter_grade": letter_grade,
            "attendance_rate": attendance_rate
        })

    return jsonify({"status": "ok", "data": result})
