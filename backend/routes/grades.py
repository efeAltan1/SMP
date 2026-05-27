from flask import Blueprint, request, jsonify, make_response
from models.grade import Grade
import numpy as np
import csv
import io


bp = Blueprint('grades', __name__)

# Accessing the GPA of the student. GPA calculation is based on scores, and the weights. The weighted average is calculated and then converted to a GPA scale.
@bp.route('/gpa', methods=['GET'])
def get_gpa():
    grades = Grade.find_all()
    if not grades:
        return jsonify({"status": "ok", "data": {"gpa": 0.0}})

    scores = np.array([g.data['score'] for g in grades])
    weights = np.array([g.data['weight'] for g in grades])

    weighted_avg = np.average(scores, weights=weights)


# GPA scale based on weighted average grades of the student. Thresholds are adjusted to reflect the commonly used grading system.
    if weighted_avg >= 97:
        gpa = 4.0
    elif weighted_avg >= 93:
        gpa = 3.8
    elif weighted_avg >= 90:
        gpa = 3.6
    elif weighted_avg >= 87:
        gpa = 3.4
    elif weighted_avg >= 83:
        gpa = 3.2
    elif weighted_avg >= 80:
        gpa = 2.9
    elif weighted_avg >= 77:
        gpa = 2.6
    elif weighted_avg >= 73:
        gpa = 2.3
    elif weighted_avg >= 70:
        gpa = 1.7
    elif weighted_avg >= 67:
        gpa = 1.3
    elif weighted_avg >= 63:
        gpa = 1.0
    elif weighted_avg >= 60:
        gpa = 0.7
    else:
        gpa = 0.0

    return jsonify({"status": "ok", "data": {"gpa": gpa, "average": round(float(weighted_avg), 2)}})



# Export all grades as a CSV file. CSV columns are id, subject_id, title, score, weight. The file "grades.csv" is downloaded when the route is accessed.
@bp.route('/export', methods=['GET'])
def export_grades():
    grades = Grade.find_all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'subject_id', 'title', 'score', 'weight'])

    for g in grades:
        d = g.to_dict()
        writer.writerow([d.get('_id'), d.get('subject_id'), d.get('title'), d.get('score'), d.get('weight')])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=grades.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

# CRUD routes for grades. 
@bp.route('/', methods=['GET'])
def get_grades():
    grades = Grade.find_all()
    return jsonify({"status": "ok", "data": [g.to_dict() for g in grades]})


@bp.route('/', methods=['POST'])
def create_grade():
    data = request.get_json()
    grade = Grade(data)
    grade.save()
    return jsonify({"status": "ok", "data": grade.to_dict()}), 201


@bp.route('/<id>', methods=['GET'])
def get_grade(id):
    grade = Grade.find_by_id(id)
    if not grade:
        return jsonify({"status": "error", "message": "grade not found"}), 404
    return jsonify({"status": "ok", "data": grade.to_dict()})


@bp.route('/<id>', methods=['PUT'])
def update_grade(id):
    grade = Grade.find_by_id(id)
    if not grade:
        return jsonify({"status": "error", "message": "grade not found"}), 404
    data = request.get_json()
    grade.data.update(data)
    grade.save()
    return jsonify({"status": "ok", "data": grade.to_dict()})


@bp.route('/<id>', methods=['DELETE'])
def delete_grade(id):
    grade = Grade.find_by_id(id)
    if not grade:
        return jsonify({"status": "error", "message": "grade not found"}), 404
    from config import db
    db[Grade.collection].delete_one({"_id": grade.data["_id"]})
    return jsonify({"status": "ok", "data": None})
