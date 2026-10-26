#!/usr/bin/env python3
"""
Run Evaluation Benchmark Script
Executes the evaluation suite on the persistent database and prints detection & privacy metrics.
"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db_connection, init_db
from backend.services.evaluation_service import EvaluationService
from backend.config import Config

def main():
    print("=" * 60)
    print("PrivacyGuard IPv6 - Autonomous Security Evaluation Suite")
    print("=" * 60)
    
    init_db(Config.DATABASE_PATH)
    conn = get_db_connection(Config.DATABASE_PATH)
    
    print("\n[+] Running test scenarios across Rogue RA, NDP anomalies & privacy boundaries...")
    results = EvaluationService.run_evaluation_suite(conn, tenant_id="tenant-alpha")
    
    cm = results["confusion_matrix"]
    print("\n" + "-" * 40)
    print("CONFUSION MATRIX:")
    print(f"  True Positives (TP):   {cm['true_positives']}")
    print(f"  False Positives (FP):  {cm['false_positives']}")
    print(f"  True Negatives (TN):   {cm['true_negatives']}")
    print(f"  False Negatives (FN):  {cm['false_negatives']}")
    print(f"  Total Test Vectors:    {cm['total_cases']}")
    
    print("\n" + "-" * 40)
    print("PERFORMANCE METRICS:")
    print(f"  Detection Rate / Recall: {results['detection_rate']}%")
    print(f"  False-Positive Rate:     {results['false_positive_rate']}%")
    print(f"  Precision:               {results['precision']}%")
    print(f"  F1 Score:                {results['f1_score']}%")
    
    pm = results["privacy_metrics"]
    print("\n" + "-" * 40)
    print("PRIVACY & ISOLATION AUDIT:")
    print(f"  Active Pseudonym Accepted:       {pm['controls_verified']['active_pseudonym_accepted']}")
    print(f"  Expired Pseudonym Rejected:      {pm['controls_verified']['expired_pseudonym_rejected']}")
    print(f"  Revoked Session Rejected:        {pm['controls_verified']['revoked_session_rejected']}")
    print(f"  Cross-Tenant Isolation Enforced: {pm['controls_verified']['cross_tenant_isolation_enforced']}")
    print("-" * 40)
    print(f"\nRun ID: {results['run_id']} recorded at {results['timestamp']}")
    conn.close()

if __name__ == "__main__":
    main()
