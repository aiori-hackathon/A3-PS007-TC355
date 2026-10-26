"""
Analytics Service
Computes operational dashboards, event volumes, security breakdowns,
and privacy metrics strictly partitioned by tenant context.
"""
from typing import Dict, Any, List

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(conn, tenant_id: str) -> Dict[str, Any]:
        """Provides high-level KPIs for the SOC dashboard header and stat cards."""
        cur = conn.cursor()

        # 1. Device count
        cur.execute("SELECT COUNT(*) FROM devices WHERE tenant_id = ?", (tenant_id,))
        total_devices = cur.fetchone()[0]

        # 2. Total events processed
        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ?", (tenant_id,))
        total_events = cur.fetchone()[0]

        # 3. Total alerts
        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ?", (tenant_id,))
        total_alerts = cur.fetchone()[0]

        # 4. Rogue RA alerts
        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'ROGUE_RA'", (tenant_id,))
        rogue_ra_alerts = cur.fetchone()[0]

        # 5. NDP Anomaly alerts
        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'NDP_ANOMALY'", (tenant_id,))
        ndp_alerts = cur.fetchone()[0]

        # 6. Active vs expired pseudonyms
        cur.execute("SELECT COUNT(*) FROM pseudonyms WHERE tenant_id = ? AND is_revoked = 0 AND datetime(expires_at) > datetime('now')", (tenant_id,))
        active_pseudonyms = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM pseudonyms WHERE tenant_id = ? AND (is_revoked = 1 OR datetime(expires_at) <= datetime('now'))", (tenant_id,))
        expired_pseudonyms = cur.fetchone()[0]

        # 7. Active sessions
        cur.execute("SELECT COUNT(*) FROM monitoring_sessions WHERE tenant_id = ? AND is_revoked = 0 AND datetime(expires_at) > datetime('now')", (tenant_id,))
        active_sessions = cur.fetchone()[0]

        return {
            "tenant_id": tenant_id,
            "total_devices": total_devices,
            "total_events": total_events,
            "total_alerts": total_alerts,
            "rogue_ra_alerts": rogue_ra_alerts,
            "ndp_alerts": ndp_alerts,
            "active_pseudonyms": active_pseudonyms,
            "expired_pseudonyms": expired_pseudonyms,
            "active_sessions": active_sessions
        }

    @staticmethod
    def get_traffic_analytics(conn, tenant_id: str) -> Dict[str, Any]:
        """Returns traffic metrics and event categorization over time."""
        cur = conn.cursor()
        
        # Events breakdown by event_type
        cur.execute("""
        SELECT event_type, COUNT(*) as count
        FROM network_events
        WHERE tenant_id = ?
        GROUP BY event_type
        ORDER BY count DESC
        """, (tenant_id,))
        by_type = [dict(r) for r in cur.fetchall()]

        # Normal vs suspicious
        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ? AND is_suspicious = 0", (tenant_id,))
        normal_events = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM network_events WHERE tenant_id = ? AND is_suspicious = 1", (tenant_id,))
        suspicious_events = cur.fetchone()[0]

        # Recent events for time series (grouped by 1-minute window or sequence)
        cur.execute("""
        SELECT strftime('%H:%M', timestamp) as time_slot,
               SUM(CASE WHEN is_suspicious = 0 THEN 1 ELSE 0 END) as normal_count,
               SUM(CASE WHEN is_suspicious = 1 THEN 1 ELSE 0 END) as suspicious_count
        FROM network_events
        WHERE tenant_id = ?
        GROUP BY time_slot
        ORDER BY time_slot DESC
        LIMIT 15
        """, (tenant_id,))
        time_series = [dict(r) for r in cur.fetchall()][::-1]

        return {
            "normal_events": normal_events,
            "suspicious_events": suspicious_events,
            "by_type": by_type,
            "time_series": time_series
        }

    @staticmethod
    def get_alert_analytics(conn, tenant_id: str) -> Dict[str, Any]:
        """Returns alert severity distribution and category breakdown."""
        cur = conn.cursor()

        cur.execute("""
        SELECT severity, COUNT(*) as count
        FROM security_alerts
        WHERE tenant_id = ?
        GROUP BY severity
        """, (tenant_id,))
        by_severity = [dict(r) for r in cur.fetchall()]

        cur.execute("""
        SELECT category, COUNT(*) as count
        FROM security_alerts
        WHERE tenant_id = ?
        GROUP BY category
        """, (tenant_id,))
        by_category = [dict(r) for r in cur.fetchall()]

        return {
            "by_severity": by_severity,
            "by_category": by_category
        }
