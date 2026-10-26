"""
Test Neighbour Discovery Protocol (NDP) Anomaly Detection
Tests rate detection: normal low-frequency NDP messages do not alert,
while high-rate bursts exceeding the threshold trigger NDP_ANOMALY alerts.
"""
import unittest
from backend.database import init_db, get_db_connection
from backend.services.ndp_detector import NDPDetector
from backend.services.event_processor import EventProcessor

class TestNDPAnomaly(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)
        self.detector = NDPDetector(default_threshold=5, default_window_seconds=10)
        self.processor = EventProcessor(ndp_detector=self.detector)

    def tearDown(self):
        self.conn.close()

    def test_normal_ndp_rate(self):
        """TEST 5: Verify that normal traffic below threshold does not generate an anomaly alert."""
        from backend.services.pseudonym_service import PseudonymService
        p_data = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", lifetime_seconds=300)
        pseudo = p_data["pseudonym"]

        # Process 2 normal messages (below threshold of 5)
        for i in range(2):
            evt = {
                "tenant_id": "tenant-alpha",
                "event_type": "NEIGHBOR_SOLICITATION",
                "pseudonym": pseudo,
                "source_ipv6": "2001:db8:1::10",
                "payload": {"threshold": 5, "window_seconds": 10}
            }
            res = self.processor.process_event(self.conn, evt)
            self.assertTrue(res["success"])
            self.assertFalse(res["is_suspicious"], "Normal NDP rate should not be suspicious.")
            self.assertFalse(res["alert_created"], "Normal traffic must not trigger an alert.")

    def test_abnormal_ndp_rate(self):
        """TEST 4: Verify that an excessive NDP event rate is detected and alerted."""
        from backend.services.pseudonym_service import PseudonymService
        p_data = PseudonymService.create_pseudonym(self.conn, "tenant-alpha", lifetime_seconds=300)
        pseudo = p_data["pseudonym"]

        # Send 6 messages in succession to exceed the threshold of 5
        alert_triggered = False
        for i in range(6):
            evt = {
                "tenant_id": "tenant-alpha",
                "event_type": "NEIGHBOR_SOLICITATION",
                "pseudonym": pseudo,
                "source_ipv6": "2001:db8:1::99",
                "payload": {"threshold": 5, "window_seconds": 10}
            }
            res = self.processor.process_event(self.conn, evt)
            if res.get("alert_created"):
                alert_triggered = True
                self.assertEqual(res["alert_info"]["category"], "NDP_ANOMALY")
                self.assertEqual(res["alert_info"]["severity"], "HIGH")

        self.assertTrue(alert_triggered, "Burst exceeding threshold must trigger NDP_ANOMALY alert.")

if __name__ == "__main__":
    unittest.main()
