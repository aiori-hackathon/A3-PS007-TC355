"""
Security Alert Model
Represents alerts triggered by Rogue RA or abnormal NDP message rates.
"""
from dataclasses import dataclass, asdict
import json
from typing import Optional, Dict, Any

@dataclass
class SecurityAlert:
    alert_id: str
    timestamp: str
    tenant_id: str
    pseudonym: Optional[str]
    category: str  # ROGUE_RA, NDP_ANOMALY, SESSION_VIOLATION, PRIVACY_EXPIRATION
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
    detection_reason: str
    evidence: Optional[Dict[str, Any]] = None
    is_acknowledged: bool = False
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        evidence = {}
        if row["evidence_json"]:
            try:
                evidence = json.loads(row["evidence_json"])
            except Exception:
                evidence = {}
        return cls(
            alert_id=row["alert_id"],
            timestamp=row["timestamp"],
            tenant_id=row["tenant_id"],
            pseudonym=row["pseudonym"],
            category=row["category"],
            severity=row["severity"],
            detection_reason=row["detection_reason"],
            evidence=evidence,
            is_acknowledged=bool(row["is_acknowledged"]),
            acknowledged_at=row["acknowledged_at"],
            acknowledged_by=row["acknowledged_by"]
        )
