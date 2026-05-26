from flask import Blueprint, request, jsonify
from models.assignment import Assignment
from datetime import datetime


bp = Blueprint('assignments', __name__)

# CRUD routes for assingmnts.
@bp.route('/upcoming', methods=['GET'])
def get_upcoming():
    assignments = Assignment.find_all()
    now = datetime.utcnow()
    upcoming = [
        a.to_dict() for a in assignments
        if datetime.fromisoformat(a.data['deadline']) >= now
        and a.data['status'] != 'completed'
    ]
    upcoming.sort(key=lambda a: a['deadline'])
    return jsonify({"status": "ok", "data": upcoming})


# 
@bp.route('/', methods=['GET'])
def get_assignments():
    assignments = Assignment.find_all()
    return jsonify({"status": "ok", "data": [a.to_dict() for a in assignments]})



@bp.route('/', methods=['POST'])
def create_assignment():
    data = request.get_json()
    assignment = Assignment(data)
    assignment.save()
    return jsonify({"status": "ok", "data": assignment.to_dict()}), 201


@bp.route('/<id>', methods=['GET'])
def get_assignment(id):
    assignment = Assignment.find_by_id(id)
    if not assignment:
        return jsonify({"status": "error", "message": "assignment not found"}), 404
    return jsonify({"status": "ok", "data": assignment.to_dict()})


@bp.route('/<id>', methods=['PUT'])
def update_assignment(id):
    assignment = Assignment.find_by_id(id)
    if not assignment:
        return jsonify({"status": "error", "message": "assignment not found"}), 404
    data = request.get_json()
    assignment.data.update(data)
    assignment.save()
    return jsonify({"status": "ok", "data": assignment.to_dict()})


@bp.route('/<id>', methods=['DELETE'])
def delete_assignment(id):
    assignment = Assignment.find_by_id(id)
    if not assignment:
        return jsonify({"status": "error", "message": "assignment not found"}), 404
    from config import db
    db[Assignment.collection].delete_one({"_id": assignment.data["_id"]})
    return jsonify({"status": "ok", "data": None})
