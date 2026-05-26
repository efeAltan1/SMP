from flask import Blueprint, jsonify, request
from models.announcement import Announcement


bp = Blueprint('announcements', __name__)

# Get all announcements, with optional tag filtering.
@bp.route('/', methods=['GET'])
def get_announcements():
    tag = request.args.get('tag')
    announcements = Announcement.find_all()
    if tag:
        announcements = [a for a in announcements if a.data.get('tag') == tag]
    return jsonify({"status": "ok", "data": [a.to_dict() for a in announcements]})

# Get a single announcement by ID.
@bp.route('/<id>', methods=['GET'])
def get_announcement(id):
    announcement = Announcement.find_by_id(id)
    if not announcement:
        return jsonify({"status": "error", "message": "announcement not found"}), 404
    return jsonify({"status": "ok", "data": announcement.to_dict()})
