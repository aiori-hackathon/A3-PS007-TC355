"""
Test Analytics Service
Verifies summary cards, traffic breakdowns, and alert distributions by tenant.
"""
import unittest
from backend.database import init_db, get_db_connection
from backend.services.analytics_service import AnalyticsService

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection(":memory:")
        init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_summary_and_traffic_aggregation(self):
        summary = AnalyticsService.get_dashboard_summary(self.conn, "tenant-alpha")
        self.assertEqual(summary["total_devices"], 5)
        self.assertGreaterEqual(summary["total_events"], 5)

        traffic = AnalyticsService.get_traffic_analytics(self.conn, "tenant-alpha")
        self.assertIn("normal_events", traffic)
        self.assertIn("suspicious_events", traffic)

        alerts = AnalyticsService.get_alert_analytics(self.conn, "tenant-alpha")
        self.assertIn("by_severity", alerts)
        self.assertIn("by_category", alerts)

if __name__ == "__main__":
    unittest.main()
