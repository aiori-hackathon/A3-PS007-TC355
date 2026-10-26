"""
Dashboard Routes
Provides aggregated status, summary cards, and latest security events for the SOC overview.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path
from backend.services.analytics_service import AnalyticsService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")

@dashboard_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PrivacyGuard IPv6",
        "version": "1.0.0",
        "backend": "Flask",
        "database": "SQLite"
    })

@dashboard_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    
    try:
        summary = AnalyticsService.get_dashboard_summary(conn, tenant_id)
        
        # Recent security alerts (filtered strictly by tenant)
        cur = conn.cursor()
        cur.execute("""
        SELECT alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, is_acknowledged
        FROM security_alerts
        WHERE tenant_id = ?
        ORDER BY timestamp DESC
        LIMIT 6
        """, (tenant_id,))
        recent_alerts = [dict(r) for r in cur.fetchall()]

        # Recent network events (filtered strictly by tenant)
        cur.execute("""
        SELECT event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, is_suspicious, status
        FROM network_events
        WHERE tenant_id = ?
        ORDER BY timestamp DESC
        LIMIT 8
        """, (tenant_id,))
        recent_events = [dict(r) for r in cur.fetchall()]

        # Monitoring status from settings
        cur.execute("SELECT value FROM app_settings WHERE key = 'monitoring_active'")
        row = cur.fetchone()
        monitoring_active = (row["value"].lower() == "true") if row else True

        return jsonify({
            "success": True,
            "tenant_id": tenant_id,
            "summary": summary,
            "monitoring_active": monitoring_active,
            "recent_alerts": recent_alerts,
            "recent_events": recent_events
        })
    finally:
        conn.close()
