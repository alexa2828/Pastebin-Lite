from flask import Flask, jsonify, request, Blueprint, abort, render_template
from pymongo.errors import ServerSelectionTimeoutError
import time
from datetime import datetime, timedelta, timezone
import os
import secrets
from pymongo.collection import ReturnDocument
from models.pastes import pastes 
from mongoengine.errors import NotUniqueError



api_bp = Blueprint('api_services', __name__, url_prefix='/api/api_services')

@api_bp.route('/api/healthz', methods=['GET'])
def healthz():
    try:
        client = request.environ.get('mongoengine.connection')
        return jsonify(status="ok"), 200
    except Exception as e:
        return jsonify({"ok": False}), 500

def now_ms():
    if os.getenv("TEST_MODE") == "1":
        header = request.headers.get("x-test-now-ms")
        if header:
            return int(header)
    return int(time.time() * 1000)


def generate_id():
    return secrets.token_urlsafe(6)


def is_expired(paste, now):
    expires_at = paste.get("expires_at")
    return expires_at is not None and now >= expires_at

    
@api_bp.route("/pastes", methods=["POST"])
def create_paste():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "content is required"}), 400

    ttl_seconds = int(data.get("ttl"))
    max_views = int(data.get("max_views"))

    if ttl_seconds is not None and (not isinstance(ttl_seconds, int) or ttl_seconds < 1):
        return jsonify({"error": "ttl_seconds must be >= 1"}), 400

    if max_views is not None and (not isinstance(max_views, int) or max_views < 1):
        return jsonify({"error": "max_views must be >= 1"}), 400

    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=ttl_seconds)

    paste_id = generate_id()

    try:
        pastes(
            paste_id=paste_id,
            content=content,
            created_at=now,
            expires_at=expires_at,
            max_views=max_views,
            views=0
        ).save()
    except NotUniqueError:
        return jsonify({"error": "Paste ID collision"}), 409

    base_url = request.host_url.rstrip("/")
    return jsonify({
        "id": paste_id,
        "url": f"{base_url}/api/api_services/view_paste/{paste_id}"
    }), 201


@api_bp.route("/pastes/<paste_id>", methods=["GET"])
def fetch_paste(paste_id):
    now = datetime.utcnow()

    paste = pastes.objects(paste_id=paste_id).first()
    if not paste:
        abort(404)

    if paste.expires_at and paste.expires_at <= now:
        abort(404)

    if paste.max_views is not None and paste.views >= paste.max_views:
        abort(404)

    pastes.objects(id=paste.id).update_one(inc__views=1)
    paste.reload()

    remaining = None
    if paste.max_views is not None:
        remaining = max(paste.max_views - paste.views, 0)

    expires_at = (
        paste.expires_at.replace(tzinfo=timezone.utc).isoformat()
        if paste.expires_at else None
    )

    return jsonify({
        "content": paste.content,
        "remaining_views": remaining,
        "expires_at": expires_at
    }), 200


@api_bp.route("/view_paste/<paste_id>", methods=["GET"])
def view_paste(paste_id):
    now = datetime.utcnow()

    paste = pastes.objects(paste_id=paste_id).first()

    if not paste:
        return render_template(
            "create.html",
            error_message="Paste not found or has been deleted."
        ), 404

    if paste.expires_at and paste.expires_at <= now:
        return render_template(
            "create.html",
            error_message="This paste has expired."
        ), 404

    if paste.max_views is not None and paste.views >= paste.max_views:
        return render_template(
            "create.html",
            error_message="This paste has reached its view limit."
        ), 404

    pastes.objects(id=paste.id).update_one(inc__views=1)
    paste.reload()

    remaining_views = None
    if paste.max_views is not None:
        remaining_views = max(paste.max_views - paste.views, 0)

    if paste.expires_at and paste.expires_at != "Never":
        expires_at = paste.expires_at.strftime("%d %b %Y, %I:%M %p")
    else:
        expires_at = "Never"

    return render_template(
        "view.html",
        paste_id=paste_id,
        content=paste["content"],
        remaining_views=remaining_views,
        expires_at=expires_at
    )