"""
Alert Routes
Allows querying, filtering, and acknowledging security alerts.
Maintains tamper-proof evidence without deleting original audit records.
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timezone
from backend.database import get_db_connection, get_db_path

alert_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

@alert_bp.route("", methods=["GET"])
def get_alerts():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    severity = request.args.get("severity")
    category = request.args.get("category")
    
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        query = """
        SELECT alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, evidence_json, is_acknowledged, acknowledged_at, acknowledged_by
        FROM security_alerts
        WHERE tenant_id = ?
        """
        params = [tenant_id]

        if severity and severity.upper() != "ALL":
            query += " AND severity = ?"
            params.append(severity.upper())

        if category and category.upper() != "ALL":
            query += " AND category = ?"
            params.append(category.upper())

        query += " ORDER BY timestamp DESC LIMIT 100"

        cur.execute(query, params)
        alerts = [dict(r) for r in cur.fetchall()]
        return jsonify({"success": True, "tenant_id": tenant_id, "alerts": alerts})
    finally:
        conn.close()

@alert_bp.route("/<alert_id>", methods=["GET"])
def get_alert_detail(alert_id):
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, evidence_json, is_acknowledged, acknowledged_at, acknowledged_by
        FROM security_alerts
        WHERE alert_id = ? AND tenant_id = ?
        """, (alert_id, tenant_id))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "error": "Alert not found in tenant scope"}), 404
        return jsonify({"success": True, "alert": dict(row)})
    finally:
        conn.close()

@alert_bp.route("/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    analyst_name = data.get("analyst", "SOC-Analyst-1")
    
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("""
        UPDATE security_alerts
        SET is_acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?
        WHERE alert_id = ? AND tenant_id = ?
        """, (now_iso, analyst_name, alert_id, tenant_id))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Alert not found or unauthorized tenant"}), 404

        return jsonify({
            "success": True,
            "message": f"Alert {alert_id} acknowledged by {analyst_name}",
            "acknowledged_at": now_iso
        })
    finally:
        conn.close()
