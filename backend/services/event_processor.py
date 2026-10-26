"""
Event Processor Service
Central ingestion and dispatch engine for simulated IPv6 network events.
Validates tenant scopes, checks pseudonym/session freshness, applies detection algorithms,
and persists events and security alerts into SQLite.
"""
import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from backend.services.pseudonym_service import PseudonymService
from backend.services.session_service import SessionService
from backend.services.ra_detector import RADetector
from backend.services.ndp_detector import NDPDetector
from backend.services.tenant_service import TenantService

class EventProcessor:
    def __init__(self, ra_detector=None, ndp_detector=None):
        self.ra_detector = ra_detector or RADetector()
        self.ndp_detector = ndp_detector or NDPDetector()

    def process_event(self, conn, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an incoming network event.
        Ensures tenant boundary checks, pseudonym validation, and detector execution.
        """
        cur = conn.cursor()
        tenant_id = event_data.get("tenant_id", "tenant-alpha")
        
        # 1. Tenant validation
        if not TenantService.is_valid_tenant(conn, tenant_id):
            return {
                "success": False,
                "error": f"Invalid tenant context: '{tenant_id}'",
                "status_code": 403
            }

        event_id = event_data.get("event_id") or f"evt_{secrets.token_hex(6)}"
        now = datetime.now(timezone.utc)
        timestamp = event_data.get("timestamp") or now.isoformat()
        event_type = event_data.get("event_type", "NDP_MESSAGE")
        pseudonym = event_data.get("pseudonym")
        source_ipv6 = event_data.get("source_ipv6")
        session_id = event_data.get("session_id")
        token = event_data.get("token")
        payload = event_data.get("payload", {})
        
        # 2. Pseudonym validation (if provided)
        if pseudonym:
            pseudo_check = PseudonymService.validate_pseudonym(conn, pseudonym, tenant_id)
            if not pseudo_check["valid"]:
                # If pseudonym expired or revoked, reject event submission
                alert_id = f"alt_{secrets.token_hex(6)}"
                cur.execute("""
                INSERT INTO security_alerts (alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, evidence_json, is_acknowledged)
                VALUES (?, ?, ?, ?, 'PRIVACY_EXPIRATION', 'MEDIUM', ?, ?, 0)
                """, (alert_id, timestamp, tenant_id, pseudonym, f"Event rejected: {pseudo_check['reason']}", json.dumps({"pseudonym": pseudonym, "tenant_id": tenant_id})))
                conn.commit()

                return {
                    "success": False,
                    "error": pseudo_check["reason"],
                    "category": "PSEUDONYM_EXPIRED",
                    "status_code": 401
                }

        # 3. Session validation (if session_id provided)
        if session_id:
            sess_check = SessionService.validate_session(conn, session_id, token, tenant_id)
            if not sess_check["valid"]:
                return {
                    "success": False,
                    "error": sess_check["reason"],
                    "category": "SESSION_EXPIRED",
                    "status_code": 401
                }

        # 4. Detector Evaluation
        is_suspicious = False
        alert_info = None

        if event_type in ("ROUTER_ADVERTISEMENT", "NORMAL_RA", "ROGUE_RA"):
            ra_res = self.ra_detector.evaluate_ra(event_data)
            if ra_res["is_rogue"]:
                is_suspicious = True
                alert_info = {
                    "category": ra_res["category"],
                    "severity": ra_res["severity"],
                    "reason": ra_res["reason"],
                    "evidence": ra_res["evidence"]
                }
        elif event_type in ("NDP_MESSAGE", "NEIGHBOR_SOLICITATION", "NEIGHBOR_ADVERTISEMENT", "ROUTER_SOLICITATION", "NDP_ANOMALY"):
            # Check custom threshold from payload or settings
            threshold = payload.get("threshold")
            window = payload.get("window_seconds")
            if threshold is None:
                cur.execute("SELECT value FROM app_settings WHERE key = 'ndp_threshold'")
                row_t = cur.fetchone()
                if row_t:
                    try:
                        threshold = int(row_t["value"])
                    except Exception:
                        threshold = None
            if window is None:
                cur.execute("SELECT value FROM app_settings WHERE key = 'ndp_window_seconds'")
                row_w = cur.fetchone()
                if row_w:
                    try:
                        window = int(row_w["value"])
                    except Exception:
                        window = None

            ndp_res = self.ndp_detector.check_ndp_rate(
                conn,
                tenant_id,
                pseudonym or source_ipv6 or "unknown",
                threshold=threshold,
                window_seconds=window
            )
            if ndp_res["is_anomaly"] or event_type == "NDP_RATE_ANOMALY":
                is_suspicious = True
                alert_info = {
                    "category": "NDP_ANOMALY",
                    "severity": "HIGH",
                    "reason": ndp_res["reason"] if ndp_res["is_anomaly"] else "NDP message rate exceeded burst threshold.",
                    "evidence": ndp_res["evidence"]
                }

        # 5. Persist Network Event
        cur.execute("""
        INSERT INTO network_events (
            event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, session_id, payload_json, is_suspicious, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PROCESSED')
        """, (
            event_id,
            timestamp,
            tenant_id,
            event_type,
            pseudonym,
            source_ipv6,
            session_id,
            json.dumps(payload),
            1 if is_suspicious else 0
        ))

        # 6. Persist Security Alert if triggered
        created_alert_id = None
        if alert_info:
            should_insert = True
            if alert_info["category"] == "NDP_ANOMALY":
                now_utc = datetime.now(timezone.utc)
                recent_window = (now_utc - timedelta(seconds=10)).isoformat()
                cur.execute("""
                SELECT alert_id FROM security_alerts
                WHERE tenant_id = ? AND category = 'NDP_ANOMALY'
                  AND pseudonym = ? AND timestamp >= ? AND is_acknowledged = 0
                """, (tenant_id, pseudonym, recent_window))
                existing_alert = cur.fetchone()
                if existing_alert:
                    should_insert = False
                    created_alert_id = existing_alert["alert_id"]

            if should_insert:
                created_alert_id = f"alt_{secrets.token_hex(6)}"
                cur.execute("""
                INSERT INTO security_alerts (
                    alert_id, timestamp, tenant_id, pseudonym, category, severity, detection_reason, evidence_json, is_acknowledged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    created_alert_id,
                    timestamp,
                    tenant_id,
                    pseudonym,
                    alert_info["category"],
                    alert_info["severity"],
                    alert_info["reason"],
                    json.dumps(alert_info["evidence"])
                ))

        # Update device last_event_at if device matched
        if pseudonym:
            cur.execute("""
            UPDATE devices
            SET last_event_at = ?
            WHERE current_pseudonym = ? AND tenant_id = ?
            """, (timestamp, pseudonym, tenant_id))

        conn.commit()

        return {
            "success": True,
            "event_id": event_id,
            "timestamp": timestamp,
            "tenant_id": tenant_id,
            "event_type": event_type,
            "is_suspicious": is_suspicious,
            "alert_created": created_alert_id is not None,
            "alert_id": created_alert_id,
            "alert_info": alert_info
        }
