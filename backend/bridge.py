#!/usr/bin/env python3
"""
CLI Bridge for PrivacyGuard IPv6
Allows Express / server.ts to invoke the real Python services and SQLite database directly.
Outputs pure JSON to stdout.
"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_connection, init_db, reset_database
from backend.config import Config
from backend.services.analytics_service import AnalyticsService
from backend.services.network_simulator import NetworkSimulator
from backend.services.pseudonym_service import PseudonymService
from backend.services.session_service import SessionService
from backend.services.evaluation_service import EvaluationService

simulator = NetworkSimulator()

def handle_request(action, args):
    db_path = Config.DATABASE_PATH
    init_db(db_path)
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    try:
        if action == "health":
            return {
                "status": "healthy",
                "service": "PrivacyGuard IPv6",
                "version": "1.0.0",
                "backend": "Python/Flask + SQLite Engine",
                "database": "SQLite"
            }

        elif action == "get_dashboard":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            summary = AnalyticsService.get_dashboard_summary(conn, tenant_id)
            
            cur.execute("""
            SELECT alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, is_acknowledged
            FROM security_alerts
            WHERE tenant_id = ?
            ORDER BY timestamp DESC
            LIMIT 6
            """, (tenant_id,))
            recent_alerts = [dict(r) for r in cur.fetchall()]

            cur.execute("""
            SELECT event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, is_suspicious, status
            FROM network_events
            WHERE tenant_id = ?
            ORDER BY timestamp DESC
            LIMIT 8
            """, (tenant_id,))
            recent_events = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT value FROM app_settings WHERE key = 'monitoring_active'")
            row = cur.fetchone()
            monitoring_active = (row["value"].lower() == "true") if row else True

            return {
                "success": True,
                "tenant_id": tenant_id,
                "summary": summary,
                "monitoring_active": monitoring_active,
                "recent_alerts": recent_alerts,
                "recent_events": recent_events
            }

        elif action == "get_devices":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("""
            SELECT device_id, tenant_id, device_name, device_type, current_ipv6, current_pseudonym, status, last_event_at, created_at
            FROM devices
            WHERE tenant_id = ?
            ORDER BY device_id ASC
            """, (tenant_id,))
            devices = [dict(r) for r in cur.fetchall()]
            return {"success": True, "tenant_id": tenant_id, "devices": devices}

        elif action == "get_device_events":
            device_id = args.get("device_id")
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("SELECT current_pseudonym FROM devices WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
            dev = cur.fetchone()
            if not dev:
                return {"success": False, "error": "Device not found"}
            pseudo = dev["current_pseudonym"]
            cur.execute("""
            SELECT event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, payload_json, is_suspicious, status
            FROM network_events
            WHERE tenant_id = ? AND pseudonym = ?
            ORDER BY timestamp DESC
            LIMIT 20
            """, (tenant_id, pseudo))
            events = [dict(r) for r in cur.fetchall()]
            return {"success": True, "device_id": device_id, "pseudonym": pseudo, "events": events}

        elif action == "rotate_address":
            device_id = args.get("device_id")
            tenant_id = args.get("tenant_id", "tenant-alpha")
            return simulator.rotate_device_address(conn, device_id, tenant_id)

        elif action == "connect_device":
            device_id = args.get("device_id")
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("UPDATE devices SET status = 'CONNECTED' WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
            conn.commit()
            return {"success": True, "device_id": device_id, "status": "CONNECTED"}

        elif action == "disconnect_device":
            device_id = args.get("device_id")
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("UPDATE devices SET status = 'DISCONNECTED' WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
            conn.commit()
            return {"success": True, "device_id": device_id, "status": "DISCONNECTED"}

        elif action == "get_monitoring_status":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("SELECT value FROM app_settings WHERE key = 'monitoring_active'")
            row = cur.fetchone()
            is_active = (row["value"].lower() == "true") if row else True

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

            return {
                "success": True,
                "tenant_id": tenant_id,
                "monitoring_active": is_active,
                "total_events": total_events,
                "normal_events": normal_events,
                "suspicious_events": suspicious_events,
                "ndp_threshold": threshold,
                "ndp_window_seconds": window
            }

        elif action == "start_monitoring":
            cur.execute("UPDATE app_settings SET value = 'true' WHERE key = 'monitoring_active'")
            conn.commit()
            return {"success": True, "monitoring_active": True}

        elif action == "stop_monitoring":
            cur.execute("UPDATE app_settings SET value = 'false' WHERE key = 'monitoring_active'")
            conn.commit()
            return {"success": True, "monitoring_active": False}

        elif action == "simulate_normal_traffic":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            count = int(args.get("count", 5))
            events = simulator.generate_normal_traffic(conn, tenant_id, count=count)
            return {
                "success": True,
                "message": f"Generated {len(events)} normal IPv6 packets",
                "events_generated": len(events)
            }

        elif action == "simulate_rogue_ra":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            source = args.get("source_ipv6", "fe80::dead:beef:666")
            prefix = args.get("advertised_prefix", "2001:db8:evil::/64")
            result = simulator.simulate_rogue_ra(conn, tenant_id, unauthorized_source=source, bogus_prefix=prefix)
            return {
                "success": True,
                "message": "Simulated Rogue Router Advertisement injected",
                "alert_generated": result.get("alert_created", False),
                "alert_id": result.get("alert_id"),
                "detection": result.get("alert_info")
            }

        elif action == "simulate_ndp_anomaly":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            burst_count = int(args.get("burst_count", 55))
            target_pseudo = args.get("pseudonym")
            result = simulator.simulate_ndp_anomaly(conn, tenant_id, burst_count=burst_count, target_pseudonym=target_pseudo)
            return {
                "success": True,
                "message": f"Simulated {burst_count} high-rate NDP packets",
                "alert_generated": result.get("alert_created", False) if result else True,
                "alert_id": result.get("alert_id") if result else None,
                "detection": result.get("alert_info") if result else None
            }

        elif action == "reset_demo":
            reset_database(db_path)
            return {"success": True, "message": "Demo state reset successfully."}

        elif action == "get_alerts":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            severity = args.get("severity")
            category = args.get("category")
            
            query = "SELECT alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, evidence_json, is_acknowledged, acknowledged_at, acknowledged_by FROM security_alerts WHERE tenant_id = ?"
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
            return {"success": True, "tenant_id": tenant_id, "alerts": alerts}

        elif action == "acknowledge_alert":
            alert_id = args.get("alert_id")
            tenant_id = args.get("tenant_id", "tenant-alpha")
            analyst = args.get("analyst", "SOC-Analyst-1")
            from datetime import datetime, timezone
            now_iso = datetime.now(timezone.utc).isoformat()
            cur.execute("""
            UPDATE security_alerts
            SET is_acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?
            WHERE alert_id = ? AND tenant_id = ?
            """, (now_iso, analyst, alert_id, tenant_id))
            conn.commit()
            return {"success": True, "message": f"Alert {alert_id} acknowledged by {analyst}"}

        elif action == "get_privacy_status":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            pseudos = PseudonymService.list_pseudonyms(conn, tenant_id)
            sessions = SessionService.list_sessions(conn, tenant_id)
            return {
                "success": True,
                "tenant_id": tenant_id,
                "summary": {
                    "active_pseudonyms": sum(1 for p in pseudos if not p["is_expired"]),
                    "expired_pseudonyms": sum(1 for p in pseudos if p["is_expired"]),
                    "active_sessions": sum(1 for s in sessions if not s["is_expired"]),
                    "expired_sessions": sum(1 for s in sessions if s["is_expired"]),
                    "tenant_isolation_enforced": True
                }
            }

        elif action == "get_pseudonyms":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            pseudos = PseudonymService.list_pseudonyms(conn, tenant_id)
            return {"success": True, "tenant_id": tenant_id, "pseudonyms": pseudos}

        elif action == "expire_pseudonym":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            pseudo = args.get("pseudonym")
            success = PseudonymService.expire_pseudonym(conn, pseudo, tenant_id)
            return {"success": success, "pseudonym": pseudo}

        elif action == "get_sessions":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            sessions = SessionService.list_sessions(conn, tenant_id)
            return {"success": True, "tenant_id": tenant_id, "sessions": sessions}

        elif action == "revoke_session":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            session_id = args.get("session_id")
            success = SessionService.revoke_session(conn, session_id, tenant_id)
            return {"success": success, "session_id": session_id}

        elif action == "get_traffic":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            data = AnalyticsService.get_traffic_analytics(conn, tenant_id)
            return {"success": True, "tenant_id": tenant_id, "data": data}

        elif action == "get_alert_analytics":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            data = AnalyticsService.get_alert_analytics(conn, tenant_id)
            return {"success": True, "tenant_id": tenant_id, "data": data}

        elif action == "get_detection":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'ROGUE_RA'", (tenant_id,))
            ra_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'NDP_ANOMALY'", (tenant_id,))
            ndp_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM security_alerts WHERE tenant_id = ? AND category = 'PRIVACY_EXPIRATION'", (tenant_id,))
            privacy_count = cur.fetchone()[0]

            return {
                "success": True,
                "tenant_id": tenant_id,
                "rogue_ra_count": ra_count,
                "ndp_anomaly_count": ndp_count,
                "privacy_expiration_count": privacy_count
            }

        elif action == "run_evaluation":
            tenant_id = args.get("tenant_id", "tenant-alpha")
            results = EvaluationService.run_evaluation_suite(conn, tenant_id=tenant_id)
            return {"success": True, "results": results}

        elif action == "get_evaluation_results":
            results = EvaluationService.get_latest_results(conn)
            return {
                "success": True,
                "has_run": results is not None,
                "results": results
            }

        elif action == "get_settings":
            cur.execute("SELECT key, value FROM app_settings")
            rows = cur.fetchall()
            settings = {r["key"]: r["value"] for r in rows}
            return {
                "success": True,
                "settings": {
                    "ndp_threshold": int(settings.get("ndp_threshold", 50)),
                    "ndp_window_seconds": int(settings.get("ndp_window_seconds", 10)),
                    "pseudonym_lifetime_seconds": int(settings.get("pseudonym_lifetime_seconds", 300)),
                    "session_lifetime_seconds": int(settings.get("session_lifetime_seconds", 180)),
                    "event_retention_days": int(settings.get("event_retention_days", 7)),
                    "simulation_speed": settings.get("simulation_speed", "1x")
                }
            }

        elif action == "update_settings":
            for k in ["ndp_threshold", "ndp_window_seconds", "pseudonym_lifetime_seconds", "session_lifetime_seconds", "event_retention_days", "simulation_speed"]:
                if k in args:
                    cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES (?, ?, datetime('now'))", (k, str(args[k])))
            conn.commit()
            return {"success": True, "message": "Settings updated"}

        else:
            return {"success": False, "error": f"Unknown action '{action}'"}

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No action specified"}))
        sys.exit(1)
        
    action_name = sys.argv[1]
    raw_args = sys.argv[2] if len(sys.argv) > 2 else "{}"
    try:
        parsed_args = json.loads(raw_args)
    except Exception:
        parsed_args = {}
        
    out = handle_request(action_name, parsed_args)
    print(json.dumps(out))
