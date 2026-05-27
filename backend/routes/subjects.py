from flask import Blueprint, jsonify
from models.subject import Subject


bp = Blueprint('subjects', __name__)


@bp.route('/', methods=['GET'])
def get_subjects():
    subjects = Subject.find_all()
    return jsonify({"status": "ok", "data": [s.to_dict() for s in subjects]})


@bp.route('/<id>', methods=['GET'])
def get_subject(id):
    subject = Subject.find_by_id(id)
    if not subject:
        return jsonify({"status": "error", "message": "subject not found"}), 404
    return jsonify({"status": "ok", "data": subject.to_dict()})
