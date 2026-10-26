"""
PrivacyGuard IPv6 - Configuration Module
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-pv6-2026")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "data" / "privacyguard.db"))
    
    # Trusted router sources and allowed prefix lists for RA validation
    TRUSTED_ROUTERS = [
        "fe80::1",
        "fe80::cafe:1",
        "2001:db8:1::1"
    ]
    ALLOWED_PREFIXES = [
        "2001:db8:1::/64",
        "fd00:pg6:cafe::/64"
    ]
    
    # Default detection thresholds (demonstration values, configurable via Settings)
    DEFAULT_NDP_THRESHOLD = 50          # Max NDP messages per window
    DEFAULT_NDP_WINDOW_SECONDS = 10     # Sliding window size
    DEFAULT_PSEUDONYM_LIFETIME = 1800   # 30 minutes in seconds for demonstration stability
    DEFAULT_SESSION_LIFETIME = 1800     # 30 minutes in seconds
    DEFAULT_RETENTION_DAYS = 7          # Event retention in days
    
    # Tenants
    DEFAULT_TENANTS = [
        {"id": "tenant-alpha", "name": "Tenant Alpha (Smart Facility A)"},
        {"id": "tenant-beta", "name": "Tenant Beta (Smart Logistics B)"}
    ]

class TestConfig(Config):
    DATABASE_PATH = ":memory:"
    DEFAULT_NDP_THRESHOLD = 10
    DEFAULT_NDP_WINDOW_SECONDS = 5
    DEFAULT_PSEUDONYM_LIFETIME = 2      # Fast expiration for unit testing
    DEFAULT_SESSION_LIFETIME = 2
