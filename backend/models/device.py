"""
Device Model
Represents an IPv6-enabled simulated IoT device scoped to a tenant.
"""
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Device:
    device_id: str
    tenant_id: str
    device_name: str
    device_type: str
    current_ipv6: str
    current_pseudonym: str
    status: str = "CONNECTED"
    last_event_at: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            device_id=row["device_id"],
            tenant_id=row["tenant_id"],
            device_name=row["device_name"],
            device_type=row["device_type"],
            current_ipv6=row["current_ipv6"],
            current_pseudonym=row["current_pseudonym"],
            status=row["status"],
            last_event_at=row["last_event_at"],
            created_at=row["created_at"]
        )
