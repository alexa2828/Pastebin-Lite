from flask import Blueprint, jsonify, request, abort, render_template
import time
from datetime import datetime, timedelta, timezone
import os
import secrets

api_bp = Blueprint('api_services', __name__, url_prefix='/api/api_services')


def get_db():
    from flask import current_app
    return current_app.config["DB"]


def now_ms():
    if os.getenv("TEST_MODE") == "1":
        header = request.headers.get("x-test-now-ms")
        if header:
            return int(header)
    return int(time.time() * 1000)


def generate_id():
    return secrets.token_urlsafe(6)


@api_bp.route('/api/healthz', methods=['GET'])
def healthz():
    try:
        # Try a simple operation to check DB connectivity
        get_db().list_collection_names()
        return jsonify(status="ok"), 200
    except Exception:
        return jsonify({"ok": False}), 500


@api_bp.route("/pastes", methods=["POST"])
def create_paste():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "content is required"}), 400

    ttl_seconds = int(data.get("ttl", 3600))
    max_views = int(data.get("max_views", 1))

    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=ttl_seconds)
    paste_id = generate_id()

    paste_doc = {
        "paste_id": paste_id,
        "content": content,
        "created_at": now,
        "expires_at": expires_at,
        "max_views": max_views,
        "views": 0
    }

    db = get_db()
    try:
        db.pastes.insert_one(paste_doc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    base_url = request.host_url.rstrip("/")
    return jsonify({
        "id": paste_id,
        "url": f"{base_url}/api/api_services/view_paste/{paste_id}"
    }), 201


@api_bp.route("/pastes/<paste_id>", methods=["GET"])
def fetch_paste(paste_id):
    now = datetime.utcnow()
    db = get_db()
    paste = db.pastes.find_one({"paste_id": paste_id})

    if not paste:
        abort(404)

    if paste.get("expires_at") and paste["expires_at"] <= now:
        abort(404)

    if paste.get("max_views") is not None and paste["views"] >= paste["max_views"]:
        abort(404)

    db.pastes.update_one({"_id": paste["_id"]}, {"$inc": {"views": 1}})
    paste = db.pastes.find_one({"_id": paste["_id"]})

    remaining = None
    if paste.get("max_views") is not None:
        remaining = max(paste["max_views"] - paste["views"], 0)

    expires_at = (
        paste["expires_at"].replace(tzinfo=timezone.utc).isoformat()
        if paste.get("expires_at") else None
    )

    return jsonify({
        "content": paste["content"],
        "remaining_views": remaining,
        "expires_at": expires_at
    }), 200


@api_bp.route("/view_paste/<paste_id>", methods=["GET"])
def view_paste(paste_id):
    now = datetime.utcnow()
    db = get_db()
    paste = db.pastes.find_one({"paste_id": paste_id})

    if not paste:
        return render_template(
            "create.html",
            error_message="Paste not found or has been deleted."
        ), 404

    if paste.get("expires_at") and paste["expires_at"] <= now:
        return render_template(
            "create.html",
            error_message="This paste has expired."
        ), 404

    if paste.get("max_views") is not None and paste["views"] >= paste["max_views"]:
        return render_template(
            "create.html",
            error_message="This paste has reached its view limit."
        ), 404

    db.pastes.update_one({"_id": paste["_id"]}, {"$inc": {"views": 1}})
    paste = db.pastes.find_one({"_id": paste["_id"]})

    remaining_views = None
    if paste.get("max_views") is not None:
        remaining_views = max(paste["max_views"] - paste["views"], 0)

    expires_at = paste["expires_at"].strftime("%d %b %Y, %I:%M %p") if paste.get("expires_at") else "Never"

    return render_template(
        "view.html",
        paste_id=paste_id,
        content=paste["content"],
        remaining_views=remaining_views,
        expires_at=expires_at
    )
