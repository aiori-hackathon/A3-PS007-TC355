"""
Privacy Routes
Manages pseudonym lifecycles, active monitoring sessions, and revoking/expiring tokens.
Never exposes plaintext bearer tokens.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path
from backend.services.pseudonym_service import PseudonymService
from backend.services.session_service import SessionService

privacy_bp = Blueprint("privacy", __name__, url_prefix="/api/privacy")

@privacy_bp.route("/status", methods=["GET"])
def get_privacy_status():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        pseudonyms = PseudonymService.list_pseudonyms(conn, tenant_id)
        sessions = SessionService.list_sessions(conn, tenant_id)

        active_pseudo = sum(1 for p in pseudonyms if not p["is_expired"])
        expired_pseudo = sum(1 for p in pseudonyms if p["is_expired"])
        active_sess = sum(1 for s in sessions if not s["is_expired"])
        expired_sess = sum(1 for s in sessions if s["is_expired"])

        return jsonify({
            "success": True,
            "tenant_id": tenant_id,
            "summary": {
                "active_pseudonyms": active_pseudo,
                "expired_pseudonyms": expired_pseudo,
                "active_sessions": active_sess,
                "expired_sessions": expired_sess,
                "tenant_isolation_enforced": True
            }
        })
    finally:
        conn.close()

@privacy_bp.route("/pseudonyms", methods=["GET"])
def get_pseudonyms():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        pseudonyms = PseudonymService.list_pseudonyms(conn, tenant_id)
        return jsonify({"success": True, "tenant_id": tenant_id, "pseudonyms": pseudonyms})
    finally:
        conn.close()

@privacy_bp.route("/pseudonyms/expire", methods=["POST"])
def expire_pseudonym():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    pseudonym = data.get("pseudonym")

    if not pseudonym:
        return jsonify({"success": False, "error": "pseudonym field is required"}), 400

    conn = get_db_connection(get_db_path(current_app))
    try:
        success = PseudonymService.expire_pseudonym(conn, pseudonym, tenant_id)
        if not success:
            return jsonify({"success": False, "error": "Pseudonym not found in tenant"}), 404
        return jsonify({
            "success": True,
            "message": f"Pseudonym {pseudonym} has been marked expired and revoked",
            "pseudonym": pseudonym
        })
    finally:
        conn.close()

@privacy_bp.route("/sessions", methods=["GET"])
def get_sessions():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        sessions = SessionService.list_sessions(conn, tenant_id)
        return jsonify({"success": True, "tenant_id": tenant_id, "sessions": sessions})
    finally:
        conn.close()

@privacy_bp.route("/sessions/revoke", methods=["POST"])
def revoke_session():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"success": False, "error": "session_id field is required"}), 400

    conn = get_db_connection(get_db_path(current_app))
    try:
        success = SessionService.revoke_session(conn, session_id, tenant_id)
        if not success:
            return jsonify({"success": False, "error": "Session not found in tenant"}), 404
        return jsonify({
            "success": True,
            "message": f"Monitoring session {session_id} has been revoked",
            "session_id": session_id
        })
    finally:
        conn.close()
