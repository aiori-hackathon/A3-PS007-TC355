"""
Monitoring Routes
Controls live monitoring loop state and retrieves real-time inspection parameters.
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timezone
from backend.database import get_db_connection, get_db_path

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")

@monitoring_bp.route("/status", methods=["GET"])
def get_status():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM app_settings WHERE key = 'monitoring_active'")
        row = cur.fetchone()
        is_active = (row["value"].lower() == "true") if row else True

        # Total counts
        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ?", (tenant_id,))
        total_events = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ? AND is_suspicious = 0", (tenant_id,))
        normal_events = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ? AND is_suspicious = 1", (tenant_id,))
        suspicious_events = cur.fetchone()[0]

        cur.execute("SELECT value FROM app_settings WHERE key = 'ndp_threshold'")
        threshold = int(cur.fetchone()[0])

        cur.execute("SELECT value FROM app_settings WHERE key = 'ndp_window_seconds'")
        window = int(cur.fetchone()[0])

        return jsonify({
            "success": True,
            "tenant_id": tenant_id,
            "monitoring_active": is_active,
            "total_events": total_events,
            "normal_events": normal_events,
            "suspicious_events": suspicious_events,
            "ndp_threshold": threshold,
            "ndp_window_seconds": window
        })
    finally:
        conn.close()

@monitoring_bp.route("/start", methods=["POST"])
def start_monitoring():
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("UPDATE app_settings SET value = 'true', updated_at = ? WHERE key = 'monitoring_active'", (now_iso,))
        conn.commit()
        return jsonify({"success": True, "monitoring_active": True, "message": "Live IPv6 monitoring activated"})
    finally:
        conn.close()

@monitoring_bp.route("/stop", methods=["POST"])
def stop_monitoring():
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("UPDATE app_settings SET value = 'false', updated_at = ? WHERE key = 'monitoring_active'", (now_iso,))
        conn.commit()
        return jsonify({"success": True, "monitoring_active": False, "message": "Live IPv6 monitoring paused"})
    finally:
        conn.close()
