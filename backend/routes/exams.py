from flask import Blueprint, jsonify
from models.exam import Exam
from datetime import datetime


bp = Blueprint('exams', __name__)


# Turkish month names to numbers for date parsing
TURKISH_MONTHS = {
    'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4,
    'Mayıs': 5, 'Haziran': 6, 'Temmuz': 7, 'Ağustos': 8,
    'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12
}


# Parses Turkish date strings like "09 Haziran 2026 Salı" into a datetime object.
def parse_turkish_date(date_str):
    try:
        parts = date_str.split()
        day = int(parts[0])
        month = TURKISH_MONTHS.get(parts[1], 0)
        year = int(parts[2])
        return datetime(year, month, day)
    except (ValueError, IndexError, AttributeError):
        return None


# Returns only upcoming exams, sorted by date.
@bp.route('/upcoming', methods=['GET'])
def get_upcoming():
    exams = Exam.find_all()
    now = datetime.utcnow()
    upcoming = []
    for e in exams:
        exam_date = parse_turkish_date(e.data.get('date', ''))
        if exam_date and exam_date >= now:
            upcoming.append(e.to_dict())
    upcoming.sort(key=lambda e: parse_turkish_date(e.get('date', '')) or datetime.max)
    return jsonify({"status": "ok", "data": upcoming})


@bp.route('/', methods=['GET'])
def get_exams():
    exams = Exam.find_all()
    return jsonify({"status": "ok", "data": [e.to_dict() for e in exams]})


@bp.route('/<id>', methods=['GET'])
def get_exam(id):
    exam = Exam.find_by_id(id)
    if not exam:
        return jsonify({"status": "error", "message": "exam not found"}), 404
    return jsonify({"status": "ok", "data": exam.to_dict()})
