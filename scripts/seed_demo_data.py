#!/usr/bin/env python3
"""
Seed Demo Data Script for PrivacyGuard IPv6
Initializes the SQLite database with 5 IoT devices per tenant and baseline configuration.
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database import init_db, reset_database, get_db_connection
from backend.config import Config

def main():
    print("=" * 60)
    print("PrivacyGuard IPv6 - Database Initialisation & Seeding")
    print("=" * 60)
    db_path = Config.DATABASE_PATH
    print(f"Target Database: {db_path}")
    
    init_db(db_path)
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT tenant_id, name FROM tenants")
    tenants = cur.fetchall()
    print(f"\n[+] Provisioned {len(tenants)} Tenants:")
    for t in tenants:
        print(f"    - {t['tenant_id']}: {t['name']}")
        
    cur.execute("SELECT tenant_id, COUNT(*) FROM devices GROUP BY tenant_id")
    dev_counts = cur.fetchall()
    print(f"\n[+] Provisioned Devices:")
    for d in dev_counts:
        print(f"    - Tenant {d[0]}: {d[1]} active IoT devices")
        
    cur.execute("SELECT COUNT(*) FROM pseudonyms")
    pseudo_count = cur.fetchone()[0]
    print(f"\n[+] Initial Cryptographic Pseudonyms: {pseudo_count}")
    
    conn.close()
    print("\nDatabase seeded successfully. Ready for demonstration!")

if __name__ == "__main__":
    main()
