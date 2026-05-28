from flask import Blueprint, jsonify
from scrapers.obis import OBISScraper
import threading

bp = Blueprint('sync', __name__)

# Tracks the last sync result so the frontend can poll for completion
_sync_state = {"status": "idle", "errors": {}}


def _run_scrape():
    _sync_state["status"] = "running"
    _sync_state["errors"] = {}
    try:
        errors = OBISScraper().scrape_all()
        _sync_state["errors"] = errors
        _sync_state["status"] = "partial" if errors else "done"
    except Exception as e:
        _sync_state["errors"] = {"fatal": str(e)}
        _sync_state["status"] = "error"


# Kicks off a background scrape immediately and returns 202.
# Prevents HTTP timeout on slow OBIS pages.
@bp.route('/', methods=['POST'])
def sync():
    if _sync_state["status"] == "running":
        return jsonify({"status": "running", "data": {"message": "sync already in progress"}}), 202
    t = threading.Thread(target=_run_scrape, daemon=True)
    t.start()
    return jsonify({"status": "started", "data": {"message": "sync started"}}), 202


# Frontend polls this until status is "done", "partial", or "error"
@bp.route('/status', methods=['GET'])
def sync_status():
    return jsonify({"status": _sync_state["status"], "errors": _sync_state["errors"]})
