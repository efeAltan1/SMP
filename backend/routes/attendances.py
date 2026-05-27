from flask import Blueprint, jsonify
from models.attendance import Attendance


bp = Blueprint('attendance', __name__)


# Parses hour strings like "13 Saat" → 13
def parse_hours(value):
    try:
        return float(value.split()[0])
    except (ValueError, AttributeError, IndexError):
        return 0.0


@bp.route('/', methods=['GET'])
def get_all_attendance():
    records = Attendance.find_all()
    return jsonify({"status": "ok", "data": [r.to_dict() for r in records]})


# Returns attendance rate for a course by code.
# Rate = 1 - (theoretical_absence / theoretical_max)
@bp.route('/<code>/rate', methods=['GET'])
def get_attendance_rate(code):
    all_records = Attendance.find_all()
    records = [r for r in all_records if r.data.get('code') == code]
    if not records:
        return jsonify({"status": "error", "message": "no attendance record found for this code"}), 404

    record = records[0]
    absence = parse_hours(record.data.get('theoretical_absence', '0'))
    max_hours = parse_hours(record.data.get('theoretical_max', '0'))
    rate = round((1 - absence / max_hours) * 100, 2) if max_hours > 0 else 100.0

    return jsonify({"status": "ok", "data": {
        "code": code,
        "theoretical_absence": record.data.get('theoretical_absence'),
        "theoretical_max": record.data.get('theoretical_max'),
        "rate": rate
    }})


@bp.route('/<code>', methods=['GET'])
def get_attendance_by_code(code):
    all_records = Attendance.find_all()
    records = [r.to_dict() for r in all_records if r.data.get('code') == code]
    if not records:
        return jsonify({"status": "error", "message": "no attendance record found for this code"}), 404
    return jsonify({"status": "ok", "data": records})
