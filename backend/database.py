"""
PrivacyGuard IPv6 - Database Layer
Uses SQLite with WAL mode, parameterized queries, and strict tenant isolation.
"""
import os
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from backend.config import Config

def get_db_path(app=None):
    if app and "DATABASE_PATH" in app.config:
        return app.config["DATABASE_PATH"]
    return Config.DATABASE_PATH

def get_db_connection(db_path=None):
    path = db_path or Config.DATABASE_PATH
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path_or_conn=None):
    if isinstance(db_path_or_conn, sqlite3.Connection):
        conn = db_path_or_conn
        should_close = False
    else:
        conn = get_db_connection(db_path_or_conn)
        should_close = True
    cur = conn.cursor()
    
    # 1. Tenants table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # 2. Devices table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        device_name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        current_ipv6 TEXT NOT NULL,
        current_pseudonym TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'CONNECTED',
        last_event_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
    )
    """)
    
    # 3. Pseudonyms table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pseudonyms (
        pseudonym TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        device_ref TEXT,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_revoked INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (pseudonym, tenant_id),
        FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
    )
    """)
    
    # 4. Monitoring sessions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_sessions (
        session_id TEXT PRIMARY KEY,
        token_hash TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        pseudonym TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_revoked INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
    )
    """)
    
    # 5. Network events table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS network_events (
        event_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        pseudonym TEXT,
        source_ipv6 TEXT,
        session_id TEXT,
        payload_json TEXT,
        is_suspicious INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'PROCESSED',
        FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
    )
    """)
    
    # 6. Security alerts table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS security_alerts (
        alert_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        pseudonym TEXT,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        detection_reason TEXT NOT NULL,
        evidence_json TEXT,
        is_acknowledged INTEGER NOT NULL DEFAULT 0,
        acknowledged_at TEXT,
        acknowledged_by TEXT,
        FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
    )
    """)
    
    # 7. Evaluation runs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_runs (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        tp INTEGER NOT NULL,
        fp INTEGER NOT NULL,
        tn INTEGER NOT NULL,
        fn INTEGER NOT NULL,
        detection_rate REAL NOT NULL,
        false_positive_rate REAL NOT NULL,
        precision REAL NOT NULL,
        f1_score REAL NOT NULL,
        metrics_json TEXT NOT NULL
    )
    """)
    
    # 8. App settings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Indexes for performance and tenant isolation
    cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_tenant ON devices (tenant_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pseudonyms_tenant ON pseudonyms (tenant_id, expires_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_tenant ON monitoring_sessions (tenant_id, expires_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_tenant_time ON network_events (tenant_id, timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_tenant_time ON security_alerts (tenant_id, timestamp)")
    
    conn.commit()
    seed_initial_data(conn)
    if should_close:
        conn.close()

def seed_initial_data(conn):
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Seed default tenants
    for tenant in Config.DEFAULT_TENANTS:
        cur.execute("""
        INSERT OR IGNORE INTO tenants (tenant_id, name, created_at)
        VALUES (?, ?, ?)
        """, (tenant["id"], tenant["name"], now_iso))
        
    # Seed default settings
    default_settings = {
        "ndp_threshold": str(Config.DEFAULT_NDP_THRESHOLD),
        "ndp_window_seconds": str(Config.DEFAULT_NDP_WINDOW_SECONDS),
        "pseudonym_lifetime_seconds": str(Config.DEFAULT_PSEUDONYM_LIFETIME),
        "session_lifetime_seconds": str(Config.DEFAULT_SESSION_LIFETIME),
        "event_retention_days": str(Config.DEFAULT_RETENTION_DAYS),
        "monitoring_active": "true"
    }
    for key, val in default_settings.items():
        cur.execute("""
        INSERT OR IGNORE INTO app_settings (key, value, updated_at)
        VALUES (?, ?, ?)
        """, (key, val, now_iso))
        
    # Seed devices for tenant-alpha if empty
    cur.execute("SELECT COUNT(*) FROM devices WHERE tenant_id = 'tenant-alpha'")
    if cur.fetchone()[0] == 0:
        seed_tenant_devices(conn, "tenant-alpha")
        
    # Seed devices for tenant-beta if empty
    cur.execute("SELECT COUNT(*) FROM devices WHERE tenant_id = 'tenant-beta'")
    if cur.fetchone()[0] == 0:
        seed_tenant_devices(conn, "tenant-beta")
        
    conn.commit()

def seed_tenant_devices(conn, tenant_id):
    import secrets
    from datetime import timedelta
    
    cur = conn.cursor()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_iso = (now + timedelta(seconds=Config.DEFAULT_PSEUDONYM_LIFETIME)).isoformat()
    
    base_types = [
        ("Temperature Sensor", "ENVIRONMENT"),
        ("Smart Lighting Controller", "LIGHTING"),
        ("Environmental Sensor", "HVAC"),
        ("Smart Gateway", "INFRASTRUCTURE"),
        ("Security Sensor", "PHYSICAL_SECURITY")
    ]
    
    prefix = "2001:db8:1" if tenant_id == "tenant-alpha" else "2001:db8:2"
    
    for idx, (dev_name, dev_type) in enumerate(base_types, start=1):
        dev_id = f"dev-{tenant_id[-5:]}-{idx:02d}"
        pseudo = f"DEV-{secrets.token_hex(2).upper()}"
        suffix = secrets.token_hex(2)
        ipv6 = f"{prefix}::{idx:02x}:{suffix}"
        
        # Register pseudonym
        cur.execute("""
        INSERT INTO pseudonyms (pseudonym, tenant_id, device_ref, created_at, expires_at, is_revoked)
        VALUES (?, ?, ?, ?, ?, 0)
        """, (pseudo, tenant_id, dev_id, now_iso, expires_iso))
        
        # Register device
        cur.execute("""
        INSERT INTO devices (device_id, tenant_id, device_name, device_type, current_ipv6, current_pseudonym, status, last_event_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'CONNECTED', ?, ?)
        """, (dev_id, tenant_id, dev_name, dev_type, ipv6, pseudo, now_iso, now_iso))
        
        # Seed an initial monitoring session
        session_id = f"sess_{secrets.token_hex(8)}"
        token = secrets.token_urlsafe(24)
        import hashlib
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        sess_expires_iso = (now + timedelta(seconds=Config.DEFAULT_SESSION_LIFETIME)).isoformat()
        
        cur.execute("""
        INSERT INTO monitoring_sessions (session_id, token_hash, tenant_id, pseudonym, created_at, expires_at, is_revoked)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (session_id, token_hash, tenant_id, pseudo, now_iso, sess_expires_iso))
        
        # Initial connect event
        event_id = f"evt_{secrets.token_hex(6)}"
        cur.execute("""
        INSERT INTO network_events (event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, session_id, payload_json, is_suspicious, status)
        VALUES (?, ?, ?, 'DEVICE_CONNECTED', ?, ?, ?, ?, 0, 'PROCESSED')
        """, (event_id, now_iso, tenant_id, pseudo, ipv6, session_id, json.dumps({"device_name": dev_name, "device_type": dev_type})))

def reset_database(db_path=None):
    """Safely reset the database by clearing demo state and reseeding clean initial devices."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM security_alerts")
    cur.execute("DELETE FROM network_events")
    cur.execute("DELETE FROM monitoring_sessions")
    cur.execute("DELETE FROM pseudonyms")
    cur.execute("DELETE FROM devices")
    cur.execute("DELETE FROM evaluation_runs")
    conn.commit()
    seed_initial_data(conn)
    conn.close()
