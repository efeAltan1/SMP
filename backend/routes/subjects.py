from flask import Blueprint, request, jsonify
from models.subject import Subject


bp = Blueprint('subjects', __name__)


# get all subjects
@bp.route('/', methods=['GET'])
def get_subjects():
    subjects = Subject.find_all()
    return jsonify({"status": "ok", "data": [s.to_dict() for s in subjects]})


# create a new subject
@bp.route('/', methods=['POST'])
def create_subject():
    data = request.get_json()
    subject = Subject(data)
    subject.save()
    return jsonify({"status": "ok", "data": subject.to_dict()}), 201


# get a single subject by id
@bp.route('/<id>', methods=['GET'])
def get_subject(id):
    subject = Subject.find_by_id(id)
    if not subject:
        return jsonify({"status": "error", "message": "subject not found"}), 404
    return jsonify({"status": "ok", "data": subject.to_dict()})


# update a subject by id
@bp.route('/<id>', methods=['PUT'])
def update_subject(id):
    subject = Subject.find_by_id(id)
    if not subject:
        return jsonify({"status": "error", "message": "subject not found"}), 404
    data = request.get_json()
    subject.data.update(data)
    subject.save()
    return jsonify({"status": "ok", "data": subject.to_dict()})


# delete a subject by id
@bp.route('/<id>', methods=['DELETE'])
def delete_subject(id):
    subject = Subject.find_by_id(id)
    if not subject:
        return jsonify({"status": "error", "message": "subject not found"}), 404
    from config import db
    db[Subject.collection].delete_one({"_id": subject.data["_id"]})
    return jsonify({"status": "ok", "data": None})
