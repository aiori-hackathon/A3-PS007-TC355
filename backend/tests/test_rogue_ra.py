"""
Test Rogue Router Advertisement (RA) Detection
Tests that legitimate RAs from trusted gateways are accepted,
while unauthorized sources or hijacked prefixes trigger CRITICAL/HIGH alerts.
"""
import unittest
from backend.database import init_db, get_db_connection
from backend.services.ra_detector import RADetector
from backend.services.event_processor import EventProcessor

class TestRogueRA(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)
        self.detector = RADetector()
        self.processor = EventProcessor(ra_detector=self.detector)

    def tearDown(self):
        self.conn.close()

    def test_legitimate_router_advertisement(self):
        """TEST 2: Verify that an authorised RA with an allowed prefix does not produce a rogue alert."""
        evt = {
            "tenant_id": "tenant-alpha",
            "event_type": "ROUTER_ADVERTISEMENT",
            "source_ipv6": "fe80::1",
            "router_id": "fe80::1",
            "advertised_prefix": "2001:db8:1::/64",
            "router_lifetime": 1800
        }
        res = self.processor.process_event(self.conn, evt)
        self.assertTrue(res["success"])
        self.assertFalse(res["is_suspicious"], "Authorised RA should not be flagged as suspicious.")
        self.assertFalse(res["alert_created"], "No security alert should be created for legitimate RA.")

    def test_rogue_router_advertisement_unauthorised_source(self):
        """TEST 3: Verify that an unauthorised RA produces a rogue router alert."""
        evt = {
            "tenant_id": "tenant-alpha",
            "event_type": "ROUTER_ADVERTISEMENT",
            "source_ipv6": "fe80::dead:beef:1234",
            "router_id": "fe80::dead:beef:1234",
            "advertised_prefix": "2001:db8:evil::/64",
            "router_lifetime": 1800
        }
        res = self.processor.process_event(self.conn, evt)
        self.assertTrue(res["success"])
        self.assertTrue(res["is_suspicious"], "Unauthorised RA must be marked suspicious.")
        self.assertTrue(res["alert_created"], "Alert must be created for rogue RA.")

        # Check alert in database
        cur = self.conn.cursor()
        cur.execute("SELECT category, severity, detection_reason FROM security_alerts WHERE alert_id = ?", (res["alert_id"],))
        alert = cur.fetchone()
        self.assertEqual(alert["category"], "ROGUE_RA")
        self.assertEqual(alert["severity"], "CRITICAL")
        self.assertIn("not in trusted router list", alert["detection_reason"])

    def test_rogue_ra_hijacked_prefix_from_trusted_source(self):
        """Verify that an authorised router advertising an unexpected prefix generates an alert."""
        evt = {
            "tenant_id": "tenant-alpha",
            "event_type": "ROUTER_ADVERTISEMENT",
            "source_ipv6": "fe80::1",
            "router_id": "fe80::1",
            "advertised_prefix": "2001:db8:rogue_prefix::/64",
            "router_lifetime": 1800
        }
        res = self.processor.process_event(self.conn, evt)
        self.assertTrue(res["is_suspicious"])
        self.assertTrue(res["alert_created"])

if __name__ == "__main__":
    unittest.main()
