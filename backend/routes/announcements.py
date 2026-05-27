from flask import Blueprint, jsonify
from models.announcement import Announcement


bp = Blueprint('announcements', __name__)


@bp.route('/', methods=['GET'])
def get_announcements():
    announcements = Announcement.find_all()
    return jsonify({"status": "ok", "data": [a.to_dict() for a in announcements]})


@bp.route('/<id>', methods=['GET'])
def get_announcement(id):
    announcement = Announcement.find_by_id(id)
    if not announcement:
        return jsonify({"status": "error", "message": "announcement not found"}), 404
    return jsonify({"status": "ok", "data": announcement.to_dict()})
