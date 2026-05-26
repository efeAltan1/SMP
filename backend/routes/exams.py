from flask import Blueprint, jsonify
from models.exam import Exam
from datetime import datetime


bp = Blueprint('exams', __name__)

# Gets all exams, with filtering for upcoming exams.
@bp.route('/upcoming', methods=['GET'])
def get_upcoming():
    exams = Exam.find_all()
    now = datetime.utcnow()
    upcoming = [
        e.to_dict() for e in exams
        if datetime.fromisoformat(e.data['date']) >= now
    ]
    upcoming.sort(key=lambda e: e['date'])
    return jsonify({"status": "ok", "data": upcoming})


@bp.route('/', methods=['GET'])
def get_exams():
    exams = Exam.find_all()
    return jsonify({"status": "ok", "data": [e.to_dict() for e in exams]})


# Get all exams, with filtering for subject_ID. Error message if it's not found.
@bp.route('/<id>', methods=['GET'])
def get_exam(id):
    exam = Exam.find_by_id(id)
    if not exam:
        return jsonify({"status": "error", "message": "exam not found"}), 404
    return jsonify({"status": "ok", "data": exam.to_dict()})
