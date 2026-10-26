"""
Analytics Routes
Delivers time series, severity distributions, and threat category aggregates.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path
from backend.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/traffic", methods=["GET"])
def get_traffic():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        data = AnalyticsService.get_traffic_analytics(conn, tenant_id)
        return jsonify({"success": True, "tenant_id": tenant_id, "data": data})
    finally:
        conn.close()

@analytics_bp.route("/alerts", methods=["GET"])
def get_alerts():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        data = AnalyticsService.get_alert_analytics(conn, tenant_id)
        return jsonify({"success": True, "tenant_id": tenant_id, "data": data})
    finally:
        conn.close()

@analytics_bp.route("/detection", methods=["GET"])
def get_detection_breakdown():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'ROGUE_RA'", (tenant_id,))
        ra_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'NDP_ANOMALY'", (tenant_id,))
        ndp_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'PRIVACY_EXPIRATION'", (tenant_id,))
        privacy_count = cur.fetchone()[0]

        return jsonify({
            "success": True,
            "tenant_id": tenant_id,
            "rogue_ra_count": ra_count,
            "ndp_anomaly_count": ndp_count,
            "privacy_expiration_count": privacy_count
        })
    finally:
        conn.close()
