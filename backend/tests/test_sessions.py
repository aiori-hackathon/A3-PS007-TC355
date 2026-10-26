"""
Test Short-Lived Monitoring Sessions
Tests session establishment, bearer token hashing, expiration, and revocation enforcement.
"""
import unittest
import time
from backend.database import init_db, get_db_connection
from backend.services.session_service import SessionService
from backend.services.event_processor import EventProcessor

class TestSessions(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)
        self.processor = EventProcessor()

    def tearDown(self):
        self.conn.close()

    def test_session_creation_and_bearer_validation(self):
        """Verify session creation and hash-based token verification."""
        sess = SessionService.create_session(self.conn, "tenant-alpha", "DEV-TEST", lifetime_seconds=60)
        self.assertIn("token", sess)
        self.assertTrue(sess["token"].startswith("pg6_"))

        # Verify raw token is NOT stored in DB (only SHA-256 hash)
        cur = self.conn.cursor()
        cur.execute("SELECT token_hash FROM monitoring_sessions WHERE session_id = ?", (sess["session_id"],))
        stored_hash = cur.fetchone()[0]
        self.assertNotEqual(stored_hash, sess["token"], "Plaintext token must not be stored in database.")

        # Validate with valid token
        val = SessionService.validate_session(self.conn, sess["session_id"], sess["token"], "tenant-alpha")
        self.assertTrue(val["valid"])

        # Validate with wrong token
        val_bad = SessionService.validate_session(self.conn, sess["session_id"], "wrong-token", "tenant-alpha")
        self.assertFalse(val_bad["valid"])

    def test_session_expiration(self):
        """TEST 8: Verify that an expired session cannot submit events."""
        sess = SessionService.create_session(self.conn, "tenant-alpha", "DEV-TEST", lifetime_seconds=1)
        time.sleep(1.2)

        val = SessionService.validate_session(self.conn, sess["session_id"], sess["token"], "tenant-alpha")
        self.assertFalse(val["valid"], "Expired session must not be valid.")
        self.assertTrue(val.get("expired", False))

        evt = {
            "tenant_id": "tenant-alpha",
            "event_type": "NDP_MESSAGE",
            "session_id": sess["session_id"],
            "token": sess["token"]
        }
        res = self.processor.process_event(self.conn, evt)
        self.assertFalse(res["success"])
        self.assertEqual(res["category"], "SESSION_EXPIRED")

    def test_session_revocation(self):
        """TEST 9: Verify that a revoked session cannot be reused."""
        sess = SessionService.create_session(self.conn, "tenant-alpha", "DEV-TEST", lifetime_seconds=300)
        
        revoked = SessionService.revoke_session(self.conn, sess["session_id"], "tenant-alpha")
        self.assertTrue(revoked)

        val = SessionService.validate_session(self.conn, sess["session_id"], sess["token"], "tenant-alpha")
        self.assertFalse(val["valid"])
        self.assertIn("revoked", val["reason"])

if __name__ == "__main__":
    unittest.main()
