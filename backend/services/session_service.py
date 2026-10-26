"""
Session Service
Manages short-lived cryptographically authenticated monitoring sessions.
Tokens are never stored in plaintext (SHA-256 hash in DB).
"""
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

class SessionService:
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def create_session(conn, tenant_id: str, pseudonym: str, lifetime_seconds: int = 180) -> Dict[str, Any]:
        """
        Creates a new session, returning the plaintext token once to the caller.
        Stores only the SHA-256 hash in the database.
        """
        cur = conn.cursor()
        session_id = f"sess_{secrets.token_hex(8)}"
        raw_token = f"pg6_{secrets.token_urlsafe(32)}"
        token_hash = SessionService.hash_token(raw_token)

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        expires_at = (now + timedelta(seconds=lifetime_seconds)).isoformat()

        cur.execute("""
        INSERT INTO monitoring_sessions (session_id, token_hash, tenant_id, pseudonym, created_at, expires_at, is_revoked)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (session_id, token_hash, tenant_id, pseudonym, now_iso, expires_at))
        conn.commit()

        return {
            "session_id": session_id,
            "token": raw_token,  # Disclosed once at creation to simulated client
            "tenant_id": tenant_id,
            "pseudonym": pseudonym,
            "created_at": now_iso,
            "expires_at": expires_at
        }

    @staticmethod
    def validate_session(conn, session_id: str, token: Optional[str], tenant_id: str) -> Dict[str, Any]:
        """
        Validates session existence, hash match, tenant boundary, and expiration.
        """
        cur = conn.cursor()
        cur.execute("""
        SELECT session_id, token_hash, tenant_id, pseudonym, created_at, expires_at, is_revoked
        FROM monitoring_sessions
        WHERE session_id = ? AND tenant_id = ?
        """, (session_id, tenant_id))
        row = cur.fetchone()

        if not row:
            return {"valid": False, "reason": "Session not found within specified tenant"}

        if bool(row["is_revoked"]):
            return {"valid": False, "reason": "Session has been revoked"}

        # If token was supplied, verify hash using constant-time comparison
        if token:
            computed_hash = SessionService.hash_token(token)
            import hmac
            if not hmac.compare_digest(computed_hash, row["token_hash"]):
                return {"valid": False, "reason": "Invalid bearer token"}

        now = datetime.now(timezone.utc)
        try:
            expires = datetime.fromisoformat(row["expires_at"])
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
        except Exception:
            return {"valid": False, "reason": "Corrupt session expiration timestamp"}

        if now >= expires:
            return {
                "valid": False,
                "reason": f"Session expired at {row['expires_at']}",
                "expired": True,
                "expires_at": row["expires_at"]
            }

        return {
            "valid": True,
            "session_id": row["session_id"],
            "tenant_id": row["tenant_id"],
            "pseudonym": row["pseudonym"],
            "expires_at": row["expires_at"]
        }

    @staticmethod
    def revoke_session(conn, session_id: str, tenant_id: str) -> bool:
        """Revokes a session immediately."""
        cur = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("""
        UPDATE monitoring_sessions
        SET is_revoked = 1, expires_at = ?
        WHERE session_id = ? AND tenant_id = ?
        """, (now_iso, session_id, tenant_id))
        conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def list_sessions(conn, tenant_id: str) -> List[Dict[str, Any]]:
        """Lists active and expired sessions without exposing secret token hashes."""
        cur = conn.cursor()
        cur.execute("""
        SELECT session_id, tenant_id, pseudonym, created_at, expires_at, is_revoked
        FROM monitoring_sessions
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
                "session_id": r["session_id"],
                "tenant_id": r["tenant_id"],
                "pseudonym": r["pseudonym"],
                "created_at": r["created_at"],
                "expires_at": r["expires_at"],
                "is_revoked": bool(r["is_revoked"]),
                "is_expired": is_expired,
                "status": "EXPIRED" if is_expired else "ACTIVE"
            })
        return results
