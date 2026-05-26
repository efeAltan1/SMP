from flask import Blueprint, jsonify
from models.attendance import Attendance


bp = Blueprint('attendance', __name__)


@bp.route('/', methods=['GET'])
def get_all_attendance():
    records = Attendance.find_all()
    return jsonify({"status": "ok", "data": [r.to_dict() for r in records]})


@bp.route('/<subject_id>/rate', methods=['GET'])
def get_attendance_rate(subject_id):
    all_records = Attendance.find_all()
    records = [r for r in all_records if r.data['subject_id'] == subject_id]
    if not records:
        return jsonify({"status": "error", "message": "no attendance records found for this subject"}), 404

    total = len(records)
    present = sum(1 for r in records if r.data['status'] == 'present')
    rate = round((present / total) * 100, 2)

    return jsonify({"status": "ok", "data": {"subject_id": subject_id, "rate": rate, "present": present, "total": total}})


@bp.route('/<subject_id>', methods=['GET'])
def get_attendance_by_subject(subject_id):
    all_records = Attendance.find_all()
    records = [r.to_dict() for r in all_records if r.data['subject_id'] == subject_id]
    if not records:
        return jsonify({"status": "error", "message": "no attendance records found for this subject"}), 404
    return jsonify({"status": "ok", "data": records})
