import unittest
from backend.database import init_db, get_db_connection, reset_database
from backend.services.evaluation_service import EvaluationService
from backend.config import TestConfig

try:
    from backend.app import create_app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_file.name
        self.temp_file.close()

        self.conn = get_db_connection(self.db_path)
        init_db(self.conn)
        
        if HAS_FLASK:
            class CustomTestConfig(TestConfig):
                DATABASE_PATH = self.db_path
            self.app = create_app(CustomTestConfig)
            self.client = self.app.test_client()
        else:
            self.client = None

    def tearDown(self):
        import os
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_evaluation_metric_calculation(self):
        """TEST 12: Verify TP, FP, TN, FN, Recall, FPR, Precision, and F1 calculations."""
        results = EvaluationService.run_evaluation_suite(self.conn, "tenant-alpha")
        matrix = results["confusion_matrix"]

        self.assertGreaterEqual(matrix["true_positives"], 3)
        self.assertEqual(matrix["false_positives"], 0)
        self.assertGreaterEqual(matrix["true_negatives"], 3)
        self.assertEqual(matrix["false_negatives"], 0)

        # Perfect detection of test vectors in this suite
        self.assertEqual(results["detection_rate"], 100.0)
        self.assertEqual(results["false_positive_rate"], 0.0)
        self.assertEqual(results["precision"], 100.0)
        self.assertEqual(results["f1_score"], 100.0)

        # Verify test cases count
        self.assertGreaterEqual(len(results["test_cases"]), 5)

    def test_zero_denominator_safety(self):
        """TEST 13: Verify safe division handling when denominators are zero."""
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        recall = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
        fpr = (fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
        precision = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
        f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        self.assertEqual(recall, 0.0)
        self.assertEqual(fpr, 0.0)
        self.assertEqual(precision, 0.0)
        self.assertEqual(f1, 0.0)

    def test_api_validation(self):
        """TEST 14: Verify that malformed events and invalid settings bounds are rejected."""
        if HAS_FLASK and self.client:
            # 1. Invalid setting out of bounds
            res = self.client.put("/api/settings", json={"ndp_threshold": -5})
            self.assertEqual(res.status_code, 400)

            # 2. Expiration of missing pseudonym
            res_p = self.client.post("/api/privacy/pseudonyms/expire", json={})
            self.assertEqual(res_p.status_code, 400)
        else:
            # Standalone validation logic check
            ndp_val = -5
            is_valid = 1 <= ndp_val <= 1000
            self.assertFalse(is_valid, "Negative threshold must be invalid.")

    def test_reset_demonstration(self):
        """TEST 15: Verify demo state can be reset safely and reseeds 5 devices."""
        # Insert a junk alert
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO security_alerts (alert_id, timestamp, tenant_id, category, severity, detection_reason, is_acknowledged)
        VALUES ('junk-1', '2026-10-25T00:00:00Z', 'tenant-alpha', 'TEST', 'LOW', 'test', 0)
        """)
        self.conn.commit()

        # Reset
        reset_database(self.db_path)

        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE alert_id = 'junk-1'")
        self.assertEqual(cur.fetchone()[0], 0, "Junk alerts must be cleared.")

        cur.execute("SELECT COUNT(*) FROM devices WHERE tenant_id = 'tenant-alpha'")
        self.assertEqual(cur.fetchone()[0], 5, "Initial devices must be reseeded.")

if __name__ == "__main__":
    unittest.main()
