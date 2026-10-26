"""
Neighbour Discovery Protocol (NDP) Anomaly Detector
Detects abnormal NDP message burst rates (Neighbor Solicitation / Neighbor Advertisement flood).
Employs a tenant-scoped sliding window algorithm to detect NDP Denial-of-Service or cache-exhaustion.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

class NDPDetector:
    def __init__(self, default_threshold: int = 50, default_window_seconds: int = 10):
        self.default_threshold = default_threshold
        self.default_window_seconds = default_window_seconds

    def check_ndp_rate(
        self,
        conn,
        tenant_id: str,
        source_identifier: str,
        threshold: int = None,
        window_seconds: int = None
    ) -> Dict[str, Any]:
        """
        Calculates NDP message rate for a given source identifier (pseudonym or source IP)
        strictly within the tenant's sliding time window.
        """
        cur = conn.cursor()
        limit_threshold = threshold if threshold is not None else self.default_threshold
        win_sec = window_seconds if window_seconds is not None else self.default_window_seconds

        now = datetime.now(timezone.utc)
        window_start = (now - timedelta(seconds=win_sec)).isoformat()

        # Count recent NDP events from this source identifier in the sliding window
        # Scoped strictly by tenant_id!
        cur.execute("""
        SELECT COUNT(*) as count
        FROM network_events
        WHERE tenant_id = ?
          AND (pseudonym = ? OR source_ipv6 = ?)
          AND event_type IN ('NDP_MESSAGE', 'NEIGHBOR_SOLICITATION', 'NEIGHBOR_ADVERTISEMENT', 'ROUTER_SOLICITATION')
          AND timestamp >= ?
        """, (tenant_id, source_identifier, source_identifier, window_start))
        
        row = cur.fetchone()
        current_count = row["count"] if row else 0

        # Include the current incoming event in the rate calculation
        effective_count = current_count + 1
        rate_per_second = round(effective_count / max(win_sec, 1), 2)
        is_anomaly = effective_count >= limit_threshold

        evidence = {
            "source": source_identifier,
            "tenant_id": tenant_id,
            "count_in_window": effective_count,
            "threshold": limit_threshold,
            "window_seconds": win_sec,
            "rate_per_sec": rate_per_second,
            "window_start": window_start
        }

        if is_anomaly:
            return {
                "is_anomaly": True,
                "severity": "HIGH",
                "category": "NDP_ANOMALY",
                "reason": f"Abnormal NDP rate detected: {effective_count} messages in {win_sec}s window (threshold: {limit_threshold}).",
                "evidence": evidence
            }

        return {
            "is_anomaly": False,
            "severity": "NONE",
            "category": "NDP_MESSAGE",
            "reason": f"Normal NDP traffic: {effective_count}/{limit_threshold} messages in {win_sec}s window.",
            "evidence": evidence
        }
