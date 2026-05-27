from flask import Blueprint, jsonify
from scrapers.obis import OBISScraper

bp = Blueprint('sync', __name__)


# Triggers a full OBIS scrape. Attaches to an existing Chrome session via CDP.
@bp.route('/', methods=['POST'])
def sync():
    try:
        scraper = OBISScraper()
        scraper.scrape_all()
        return jsonify({"status": "ok", "data": {"message": "sync complete"}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
