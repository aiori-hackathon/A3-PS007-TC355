"""
Network Event Model
Represents processed IPv6 ICMPv6 / NDP / RA events.
"""
from dataclasses import dataclass, asdict
import json
from typing import Optional, Dict, Any

@dataclass
class NetworkEvent:
    event_id: str
    timestamp: str
    tenant_id: str
    event_type: str
    pseudonym: Optional[str] = None
    source_ipv6: Optional[str] = None
    session_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    is_suspicious: bool = False
    status: str = "PROCESSED"

    def to_dict(self):
        d = asdict(self)
        return d

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        payload = {}
        if row["payload_json"]:
            try:
                payload = json.loads(row["payload_json"])
            except Exception:
                payload = {}
        return cls(
            event_id=row["event_id"],
            timestamp=row["timestamp"],
            tenant_id=row["tenant_id"],
            event_type=row["event_type"],
            pseudonym=row["pseudonym"],
            source_ipv6=row["source_ipv6"],
            session_id=row["session_id"],
            payload=payload,
            is_suspicious=bool(row["is_suspicious"]),
            status=row["status"]
        )
