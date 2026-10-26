"""
Test Pseudonym Lifecycle and Privacy Guarantees
Tests that temporary pseudonyms are generated securely, expire as configured,
and are strictly rejected for subsequent events upon expiration.
"""
import unittest
import time
from backend.database import init_db, get_db_connection
from backend.services.pseudonym_service import PseudonymService
from backend.services.event_processor import EventProcessor

class TestPseudonyms(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)
        self.processor = EventProcessor()

    def tearDown(self):
        self.conn.close()

    def test_pseudonym_generation_and_active_validation(self):
        """Verify pseudonym creation format and active validity check."""
        res = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", lifetime_seconds=100)
        pseudo = res["pseudonym"]
        self.assertTrue(pseudo.startswith("DEV-"))

        val = PseudonymService.validate_pseudonym(self.conn, pseudo, "tenant-alpha")
        self.assertTrue(val["valid"], "Newly created pseudonym should be valid.")

    def test_pseudonym_expiration_rejection(self):
        """TEST 7: Verify that an expired pseudonym is rejected for new monitoring events."""
        # Create a pseudonym with 1-second lifetime
        res = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", lifetime_seconds=1)
        pseudo = res["pseudonym"]

        # Wait for expiration
        time.sleep(1.2)

        # 1. Validation check
        val = PseudonymService.validate_pseudonym(self.conn, pseudo, "tenant-alpha")
        self.assertFalse(val["valid"], "Expired pseudonym must not be valid.")
        self.assertTrue(val.get("expired", False))

        # 2. Event processing check - must be rejected
        evt = {
            "tenant_id": "tenant-alpha",
            "event_type": "NDP_MESSAGE",
            "pseudonym": pseudo,
            "source_ipv6": "2001:db8:1::10"
        }
        proc_res = self.processor.process_event(self.conn, evt)
        self.assertFalse(proc_res["success"], "Event using expired pseudonym must be rejected.")
        self.assertEqual(proc_res["category"], "PSEUDONYM_EXPIRED")

    def test_manual_pseudonym_revocation(self):
        """TEST 16: Verify that explicitly revoking a pseudonym invalidates it immediately."""
        res = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", lifetime_seconds=300)
        pseudo = res["pseudonym"]

        revoked = PseudonymService.expire_pseudonym(self.conn, pseudo, "tenant-alpha")
        self.assertTrue(revoked)

        val = PseudonymService.validate_pseudonym(self.conn, pseudo, "tenant-alpha")
        self.assertFalse(val["valid"])
        self.assertIn("revoked", val["reason"])

if __name__ == "__main__":
    unittest.main()
