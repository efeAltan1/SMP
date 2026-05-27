from flask import Blueprint, request, jsonify
from models.subject import Subject

bp = Blueprint('subjects', __name__)


