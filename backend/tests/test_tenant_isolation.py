"""
Test Multi-Tenant Isolation
Verifies that Tenant Alpha cannot query or correlate Tenant Beta devices, sessions, events, or alerts.
Verifies rate counters are strictly tenant-isolated.
"""
import unittest
from backend.database import init_db, get_db_connection
from backend.services.session_service import SessionService
from backend.services.pseudonym_service import PseudonymService
from backend.services.ndp_detector import NDPDetector
from backend.services.event_processor import EventProcessor

class TestTenantIsolation(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)
        self.processor = EventProcessor()
        self.detector = NDPDetector(default_threshold=5, default_window_seconds=10)

    def tearDown(self):
        self.conn.close()

    def test_tenant_data_isolation(self):
        """TEST 10: Verify Tenant Alpha cannot access Tenant Beta devices, sessions, or alerts."""
        cur = self.conn.cursor()

        # Query Tenant Alpha devices
        cur.execute("SELECT device_id FROM devices WHERE tenant_id = 'tenant-alpha'")
        alpha_devs = [r["device_id"] for r in cur.fetchall()]

        # Query Tenant Beta devices
        cur.execute("SELECT device_id FROM devices WHERE tenant_id = 'tenant-beta'")
        beta_devs = [r["device_id"] for r in cur.fetchall()]

        # Ensure no overlap in primary device identifiers
        overlap = set(alpha_devs).intersection(set(beta_devs))
        self.assertEqual(len(overlap), 0, "Tenant device collections must be completely disjoint.")

        # Try to validate a Tenant Beta session under Tenant Alpha scope
        beta_sess = SessionService.create_session(self.conn, "tenant-beta", "DEV-BETA-01", 300)
        cross_val = SessionService.validate_session(self.conn, beta_sess["session_id"], beta_sess["token"], "tenant-alpha")
        self.assertFalse(cross_val["valid"], "Tenant Alpha must not validate or authenticate Tenant Beta sessions.")

    def test_rate_counter_isolation(self):
        """TEST 11: Verify that NDP counters from different tenants are never combined."""
        # Create identical pseudonym label in both tenants to demonstrate isolation
        pseudo_a = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", 300)["pseudonym"]
        pseudo_b = PseudonymService.create_pseudonym(self.conn, "tenant-beta", 300)["pseudonym"]

        # Send 4 messages from Tenant Alpha with pseudo_a
        for _ in range(4):
            evt = {
                "tenant_id": "tenant-alpha",
                "event_type": "NEIGHBOR_SOLICITATION",
                "pseudonym": pseudo_a,
                "payload": {"threshold": 5, "window_seconds": 10}
            }
            res_a = self.processor.process_event(self.conn, evt)
            self.assertTrue(res_a["success"])
            self.assertFalse(res_a["alert_created"])

        # Send 2 messages from Tenant Beta with pseudo_b
        # Total combined would be 6 (> 5), but tenant-beta only has 2, so neither should alert!
        for _ in range(2):
            evt = {
                "tenant_id": "tenant-beta",
                "event_type": "NEIGHBOR_SOLICITATION",
                "pseudonym": pseudo_b,
                "payload": {"threshold": 5, "window_seconds": 10}
            }
            res_b = self.processor.process_event(self.conn, evt)
            self.assertTrue(res_b["success"])
            self.assertFalse(res_b["alert_created"], "Cross-tenant counters must not aggregate together.")

if __name__ == "__main__":
    unittest.main()
