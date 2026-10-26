# PrivacyGuard IPv6 — System Architecture

**Hackathon Problem Statement:** PS-007: Privacy-Aware IPv6 IoT Security Monitoring  
**System Name:** PrivacyGuard IPv6  

---

## 1. Architectural Philosophy

Traditional Network Intrusion Detection Systems (NIDS) rely on permanent MAC addresses, static IPv6 interface identifiers (EUI-64), and unencrypted host identities. In modern IPv6 Internet of Things (IoT) deployments, exposing permanent device identifiers across local monitoring platforms creates serious privacy risks, allowing malicious network observers or compromised monitoring agents to profile, track, and correlate IoT nodes.

**PrivacyGuard IPv6** introduces a dual-layer cybersecurity and privacy framework:
1. **Zero-Trust Ephemeral Device Pseudonymization:** IoT nodes interact with the monitoring plane using cryptographically unpredictable, rotating pseudonyms (`DEV-XXXX`) and short-lived bearer session tokens (hashed via SHA-256).
2. **Deterministic ICMPv6 Threat Detection:** Specialized anomaly engines monitor IPv6 local area network traffic to detect **Rogue Router Advertisements (RA)** and **Neighbour Discovery Protocol (NDP) flooding/table exhaustion**.
3. **Multi-Tenant Cryptographic Isolation:** Strict boundary filtering ensures that telemetry, pseudonyms, sessions, and detection rate counters are never combined across operational tenants.

---

## 2. High-Level System Architecture

```
+-------------------------------------------------------------------------------+
|                       REACT / VITE SOC DASHBOARD                              |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
|   |  Live Topbar  |  | 5-Device Grid |  | Threat Charts |  | Privacy Center|  |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
+---------------------------------------+---------------------------------------+
                                        | REST API (Fetch / CORS)
                                        v
+-------------------------------------------------------------------------------+
|                        FLASK REST API & INGESTION                             |
|   +-----------------------+  +-----------------------+  +------------------+  |
|   |  /api/simulation/*    |  |  /api/monitoring/*    |  |  /api/privacy/*  |  |
|   +-----------------------+  +-----------------------+  +------------------+  |
|   +-----------------------+  +-----------------------+  +------------------+  |
|   |  /api/devices/*       |  |  /api/alerts/*         |  |  /api/eval/*     |  |
|   +-----------------------+  +-----------------------+  +------------------+  |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|      THREAT DETECTION ENGINE    |           |    PRIVACY & SESSION SERVICE    |
| - RADetector:                   |           | - PseudonymService:             |
|   * Trusted router whitelist    |           |   * Cryptographic randomness    |
|   * Allowed prefix enforcement  |           |   * Configurable TTL expiration |
| - NDPDetector:                  |           | - SessionService:               |
|   * Sliding-window rate limiter |           |   * SHA-256 token hashing       |
|   * Tenant-isolated counters    |           |   * Instant revocation          |
+---------------------------------+           +---------------------------------+
                 \                                             /
                  \                                           /
                   +--------------------+--------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                      SQLITE LIGHTWEIGHT PERSISTENCE                           |
|  - tenants (tenant_id, name)                                                  |
|  - devices (device_id, tenant_id, current_ipv6, current_pseudonym, status)    |
|  - pseudonyms (pseudonym, tenant_id, created_at, expires_at, is_revoked)      |
|  - monitoring_sessions (session_id, token_hash, tenant_id, expires_at)        |
|  - network_events (event_id, timestamp, tenant_id, type, pseudonym, ipv6)    |
|  - security_alerts (alert_id, tenant_id, category, severity, evidence)       |
|  - evaluation_runs (run_id, tp, fp, tn, fn, recall, fpr, precision, f1)       |
|  - app_settings (key, value, updated_at)                                      |
+-------------------------------------------------------------------------------+
```

---

## 3. Core Component Modules

### A. IPv6 Address & SLAAC Rotation Service (`ipv6_address_service.py`)
- Emulates RFC 4941 (Privacy Extensions for Stateless Address Autoconfiguration in IPv6).
- Devices rotate their temporary 64-bit interface identifiers randomly while maintaining subnet prefix consistency.
- **Critical Policy:** Address rotation alone does NOT flag security anomalies.

### B. Ephemeral Pseudonym Service (`pseudonym_service.py`)
- Generates 16-bit entropy hexadecimal identifiers (e.g., `DEV-A81F`).
- Scoped to tenant and monitoring lifetime (default 300 seconds).
- Expired pseudonyms are strictly rejected for new authenticated events.
- Never reveals permanent hardware identifiers (MAC/EUI-64).

### C. Short-Lived Session Service (`session_service.py`)
- Issues random session tokens (`pg6_...`).
- Stores only SHA-256 hashes in SQLite; raw tokens are never persisted or returned in listing APIs.
- Instant validation and revocation.

### D. Rogue Router Advertisement Detector (`ra_detector.py`)
- Verifies ICMPv6 Type 134 packets against:
  1. Authorised Router Gateway Source Addresses (e.g. `fe80::1`, `2001:db8:1::1`).
  2. Advertised Subnet Prefix Whitelist (e.g. `2001:db8:1::/64`).
- Unauthorised source $\rightarrow$ **CRITICAL** Rogue RA Alert.
- Advertised foreign prefix $\rightarrow$ **HIGH** Prefix Hijack Alert.

### E. NDP Rate Anomaly Detector (`ndp_detector.py`)
- Monitors ICMPv6 Neighbor Solicitation (NS) and Neighbor Advertisement (NA) frequencies.
- Evaluates event volume within a tenant-scoped sliding window (default: 50 msgs / 10s).
- Protects IoT networks from cache-exhaustion and Denial-of-Service attacks.

### F. Multi-Tenant Boundary Enforcement (`tenant_service.py`)
- Strict partition between `tenant-alpha` and `tenant-beta`.
- Cross-tenant requests are denied at ingestion.
- Rate counters are maintained per tenant to prevent cross-tenant resource skewing.

### G. Evaluation Engine (`evaluation_service.py`)
- Evaluates ground-truth test vectors across Rogue RA, NDP burst attacks, legitimate traffic, and privacy control boundaries.
- Produces mathematically verified Confusion Matrix and KPI scores.
