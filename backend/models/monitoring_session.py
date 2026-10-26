"""
Monitoring Session Model
Represents short-lived authenticated monitoring sessions.
Tokens are stored as SHA-256 hashes.
"""
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class MonitoringSession:
    session_id: str
    token_hash: str
    tenant_id: str
    pseudonym: str
    created_at: str
    expires_at: str
    is_revoked: bool = False

    def to_safe_dict(self):
        """Returns session details without disclosing the secret token or hash."""
        return {
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "pseudonym": self.pseudonym,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_revoked": self.is_revoked
        }

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            session_id=row["session_id"],
            token_hash=row["token_hash"],
            tenant_id=row["tenant_id"],
            pseudonym=row["pseudonym"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            is_revoked=bool(row["is_revoked"])
        )
