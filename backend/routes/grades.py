from flask import Blueprint, jsonify, make_response
from models.grade import Grade
import csv
import io


bp = Blueprint('grades', __name__)


# Turkish letter grade to GPA point mapping
LETTER_TO_GPA = {
    'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5,
    'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'FF': 0.0,
    'DZ': 0.0, 'G': 4.0
}


# Calculates GPA from letter grades and credits. Only includes courses with a final letter grade.
@bp.route('/gpa', methods=['GET'])
def get_gpa():
    grades = Grade.find_all()
    graded = [g for g in grades if g.data.get('letter_grade') in LETTER_TO_GPA]
    if not graded:
        return jsonify({"status": "ok", "data": {"gpa": 0.0}})

    total_points = 0.0
    total_credits = 0.0

    for g in graded:
        points = LETTER_TO_GPA[g.data['letter_grade']]
        try:
            credits = float(g.data.get('credits', 0))
        except (ValueError, TypeError):
            credits = 0.0
        total_points += points * credits
        total_credits += credits

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    return jsonify({"status": "ok", "data": {"gpa": gpa}})


# Export all grades as CSV
@bp.route('/export', methods=['GET'])
def export_grades():
    grades = Grade.find_all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['code', 'subject', 'semester', 'midterm', 'final', 'letter_grade', 'credits', 'ects'])
    for g in grades:
        d = g.to_dict()
        writer.writerow([
            d.get('code'), d.get('subject'), d.get('semester'),
            d.get('midterm'), d.get('final'), d.get('letter_grade'),
            d.get('credits'), d.get('ects')
        ])
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=grades.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@bp.route('/', methods=['GET'])
def get_grades():
    grades = Grade.find_all()
    return jsonify({"status": "ok", "data": [g.to_dict() for g in grades]})


@bp.route('/<id>', methods=['GET'])
def get_grade(id):
    grade = Grade.find_by_id(id)
    if not grade:
        return jsonify({"status": "error", "message": "grade not found"}), 404
    return jsonify({"status": "ok", "data": grade.to_dict()})
