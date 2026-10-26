"""
Pseudonym Service
Provides cryptographically secure, tenant-scoped, short-lived device pseudonyms.
Prevents cross-tenant correlation and eliminates permanent identifiers from telemetry.
"""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

class PseudonymService:
    @staticmethod
    def generate_pseudonym_label() -> str:
        """Generates an unpredictable 16-bit hex pseudonym e.g., DEV-B48F."""
        token = secrets.token_hex(2).upper()
        return f"DEV-{token}"

    @staticmethod
    def create_pseudonym(conn, tenant_id: str, lifetime_seconds: int = 300, device_ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Registers a new short-lived pseudonym for a tenant.
        """
        cur = conn.cursor()
        pseudonym = PseudonymService.generate_pseudonym_label()
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        expires_at = (now + timedelta(seconds=lifetime_seconds)).isoformat()

        cur.execute("""
        INSERT INTO pseudonyms (pseudonym, tenant_id, device_ref, created_at, expires_at, is_revoked)
        VALUES (?, ?, ?, ?, ?, 0)
        """, (pseudonym, tenant_id, device_ref, now_iso, expires_at))
        conn.commit()

        return {
            "pseudonym": pseudonym,
            "tenant_id": tenant_id,
            "created_at": now_iso,
            "expires_at": expires_at,
            "is_revoked": False,
            "is_active": True
        }

    @staticmethod
    def validate_pseudonym(conn, pseudonym: str, tenant_id: str) -> Dict[str, Any]:
        """
        Validates whether a pseudonym exists, belongs to tenant, is not revoked, and is not expired.
        """
        cur = conn.cursor()
        cur.execute("""
        SELECT pseudonym, tenant_id, created_at, expires_at, is_revoked
        FROM pseudonyms
        WHERE pseudonym = ? AND tenant_id = ?
        """, (pseudonym, tenant_id))
        row = cur.fetchone()

        if not row:
            return {"valid": False, "reason": "Pseudonym does not exist in tenant scope"}

        if bool(row["is_revoked"]):
            return {"valid": False, "reason": "Pseudonym has been explicitly revoked"}

        now = datetime.now(timezone.utc)
        try:
            expires = datetime.fromisoformat(row["expires_at"])
            # Ensure timezone-aware comparison
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
        except Exception:
            return {"valid": False, "reason": "Corrupt pseudonym expiration timestamp"}

        if now >= expires:
            return {
                "valid": False,
                "reason": f"Pseudonym expired at {row['expires_at']}",
                "expired": True,
                "expires_at": row["expires_at"]
            }

        return {
            "valid": True,
            "pseudonym": row["pseudonym"],
            "tenant_id": row["tenant_id"],
            "expires_at": row["expires_at"]
        }

    @staticmethod
    def expire_pseudonym(conn, pseudonym: str, tenant_id: str) -> bool:
        """Explicitly expires/revokes a pseudonym within a tenant."""
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("""
        UPDATE pseudonyms
        SET is_revoked = 1, expires_at = ?
        WHERE pseudonym = ? AND tenant_id = ?
        """, (now_iso, pseudonym, tenant_id))
        conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def list_pseudonyms(conn, tenant_id: str) -> List[Dict[str, Any]]:
        """Lists active and expired pseudonyms for a given tenant."""
        cur = conn.cursor()
        cur.execute("""
        SELECT pseudonym, tenant_id, created_at, expires_at, is_revoked
        FROM pseudonyms
        WHERE tenant_id = ?
        ORDER BY created_at DESC
        LIMIT 50
        """, (tenant_id,))
        rows = cur.fetchall()

        now = datetime.now(timezone.utc)
        results = []
        for r in rows:
            try:
                exp = datetime.fromisoformat(r["expires_at"])
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                is_expired = now >= exp or bool(r["is_revoked"])
            except Exception:
                is_expired = True

            results.append({
                "pseudonym": r["pseudonym"],
                "tenant_id": r["tenant_id"],
                "created_at": r["created_at"],
                "expires_at": r["expires_at"],
                "is_revoked": bool(r["is_revoked"]),
                "is_expired": is_expired,
                "status": "EXPIRED" if is_expired else "ACTIVE"
            })
        return results
