# PrivacyGuard IPv6 — Privacy-Aware IPv6 IoT Security Monitoring System

**Hackathon:** AIORI 3 Hackathon  
**Problem Statement:** PS-007: Privacy-Aware IPv6 IoT Security Monitoring  
**Target Platform:** Windows 10/11 (PowerShell) & Linux / Cloud Workstations  
**Architecture:** Full-Stack Decoupled (React 19 + Vite + Recharts / Python 3.11 Flask + SQLite)

---

## 1. Project Overview & Problem Description

The proliferation of IPv6-enabled Internet of Things (IoT) devices in smart buildings, industrial facilities, and municipal infrastructure has introduced significant security and privacy dilemmas:

1. **Privacy & Identity Leakage:** In standard IPv6 networks, devices using traditional SLAAC with static interface identifiers (IEEE EUI-64 derived from hardware MAC addresses) can be fingerprinted, profiled, and tracked over time by observers or compromised monitoring agents.
2. **ICMPv6 Rogue Router Advertisement (RA) Attacks:** Malicious actors or misconfigured routers can inject unauthorized ICMPv6 Type 134 packets, poisoning default gateways, blackholing traffic, or redirecting node traffic through adversary-controlled prefixes.
3. **Neighbour Discovery Protocol (NDP) Denial of Service:** IPv6 nodes rely on Neighbor Solicitation (NS) and Neighbor Advertisement (NA) for link-layer address resolution. Floods of bogus NDP queries can exhaust router and sensor neighbor cache tables, crashing resource-constrained IoT nodes.
4. **Cross-Tenant Telemetry Pollution:** Multi-tenant environments often lack cryptographic partitioning, risking data leakage and false attack cross-contamination.

**PrivacyGuard IPv6** resolves these challenges by introducing:
- **Zero-Trust Ephemeral Device Pseudonymization:** Nodes interact with the monitoring plane through cryptographically unpredictable, rotating pseudonyms (`DEV-XXXX`) with configurable TTL expirations.
- **RFC 4941 Temporary Address Rotation:** Nodes periodically rotate their 64-bit SLAAC interface identifiers without triggering false-positive intrusion alarms.
- **Short-Lived Authenticated Sessions:** Bearer tokens are stored exclusively as SHA-256 hashes in SQLite, ensuring immediate expiration and zero token leakage.
- **Dual Anomaly Detection Engines:** Dedicated detectors evaluate ICMPv6 Router Advertisements and sliding-window NDP message frequencies.
- **Strict Multi-Tenant Cryptographic Isolation:** Strict boundary filtering ensures Tenant Alpha and Tenant Beta records, rate counters, and security alerts remain disjoint.
- **Transparent Evaluation Benchmarking:** Ground-truth test vectors measure Detection Rate (Recall), False-Positive Rate, Precision, and F1 Score with division-by-zero protection.

---

## 2. Technology Stack

- **Frontend:** React 19, Vite, Tailwind CSS, Lucide React, Recharts (Area & Bar analytics charts).
- **Backend:** Python 3.11, Flask, Flask-CORS, SQLite (WAL mode, parameterized queries, indexes), Python Standard Library (`secrets`, `hashlib`, `hmac`).
- **Testing:** Pytest / Python standard `unittest` (20 automated unit and integration tests).
- **Network Simulator:** Python-based simulation of 5 IoT device roles, SLAAC address rotation, ICMPv6 RA messages, and NDP flood patterns.

---

## 3. Project Directory Structure

```
PrivacyGuard-IPv6/
├── README.md                          # Comprehensive system documentation & setup guide
├── .gitignore                         # Python, SQLite, Node, and IDE ignore rules
├── .env.example                       # Safe environment variable configuration template
├── requirements.txt                   # Root Python dependencies
├── package.json                       # Node.js frontend & full-stack dependencies
├── PrivacyGuard-IPv6.zip              # Pre-packaged downloadable repository archive
│
├── backend/
│   ├── app.py                         # Flask application factory, blueprints & CORS
│   ├── config.py                      # Router whitelist, allowed prefixes & defaults
│   ├── database.py                    # SQLite schema, indexes & idempotent seeder
│   ├── bridge.py                      # High-speed CLI IPC bridge for live preview
│   ├── requirements.txt               # Backend Python dependencies
│   ├── data/
│   │   ├── .gitkeep
│   │   └── privacyguard.db            # SQLite database file
│   ├── models/
│   │   ├── __init__.py
│   │   ├── device.py                  # IoT Device dataclass
│   │   ├── network_event.py           # Network event dataclass
│   │   ├── security_alert.py          # Security alert dataclass
│   │   └── monitoring_session.py      # Authenticated session dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ipv6_address_service.py    # RFC 4941 SLAAC address rotation
│   │   ├── pseudonym_service.py       # Ephemeral pseudonym generation & TTL
│   │   ├── session_service.py         # SHA-256 hashed bearer sessions
│   │   ├── tenant_service.py          # Multi-tenant boundary enforcement
│   │   ├── ra_detector.py             # Rogue Router Advertisement detector
│   │   ├── ndp_detector.py            # Sliding-window NDP rate anomaly detector
│   │   ├── event_processor.py         # Central ingestion pipeline & alert dispatcher
│   │   ├── network_simulator.py       # 5 IoT devices & attack vector generator
│   │   ├── analytics_service.py       # SOC dashboard aggregation & metrics
│   │   └── evaluation_service.py      # Ground-truth benchmark matrix & calculations
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard_routes.py        # /api/dashboard & /api/health
│   │   ├── device_routes.py           # /api/devices/* (rotate, connect, disconnect)
│   │   ├── monitoring_routes.py       # /api/monitoring/* (status, start, stop)
│   │   ├── simulation_routes.py       # /api/simulation/* (rogue-ra, ndp-anomaly, reset)
│   │   ├── alert_routes.py            # /api/alerts/* (query, filter, acknowledge)
│   │   ├── privacy_routes.py          # /api/privacy/* (pseudonyms, sessions, revoke)
│   │   ├── analytics_routes.py        # /api/analytics/* (traffic, alerts, detection)
│   │   └── evaluation_routes.py       # /api/evaluation/* (run, results)
│   └── tests/
│       ├── __init__.py
│       ├── test_devices.py            # Test 1 (initialisation) & Test 6 (rotation)
│       ├── test_rogue_ra.py           # Test 2 (legit RA) & Test 3 (rogue RA alert)
│       ├── test_ndp_anomaly.py        # Test 4 (NDP flood) & Test 5 (normal NDP)
│       ├── test_pseudonyms.py         # Test 7 (expiration) & Test 16 (revocation)
│       ├── test_sessions.py           # Test 8 (expiration) & Test 9 (revocation)
│       ├── test_tenant_isolation.py   # Test 10 (cross-tenant) & Test 11 (rate counters)
│       ├── test_analytics.py          # Analytics aggregations & KPIs
│       └── test_evaluation.py         # Test 12 (metrics), 13 (zero div), 14, 15 (reset)
│
├── frontend/
│   ├── package.json                   # Frontend dependencies
│   ├── index.html                     # HTML5 SOC dashboard entry point
│   ├── vite.config.js                 # Vite build configuration
│   └── src/
│       ├── main.jsx                   # React 19 bootstrap
│       ├── App.jsx                    # Top-level state orchestrator & navigation
│       ├── index.css                  # Tailwind styles
│       ├── App.css                    # SOC custom scrollbars & glowing cards
│       ├── components/
│       │   ├── Header.jsx             # Status badge, clock, tenant switcher & export
│       │   ├── Sidebar.jsx            # 8 SOC pages & hot-action deck
│       │   ├── StatCard.jsx           # KPI metrics card
│       │   ├── DeviceTable.jsx        # 5 IoT nodes with RFC 4941 rotation actions
│       │   ├── AlertTable.jsx         # Security incident logs & audit actions
│       │   ├── TrafficChart.jsx       # Recharts temporal traffic volume
│       │   ├── DetectionChart.jsx     # Recharts threat distribution breakdown
│       │   ├── PrivacyPanel.jsx       # Pseudonyms registry & TTL expiration
│       │   ├── SessionStatus.jsx      # SHA-256 hashed sessions audit
│       │   ├── TenantIsolationPanel.jsx # Disjoint tenant verification
│       │   ├── LoadingSpinner.jsx     # SOC loader
│       │   ├── ErrorMessage.jsx       # Backend connection alert
│       │   └── EmptyState.jsx         # Clean state presentation
│       ├── pages/
│       │   ├── Dashboard.jsx          # SOC overview & stat cards
│       │   ├── Devices.jsx            # 5 IoT device fleet & telemetry history
│       │   ├── Monitoring.jsx         # Live inspection stream & attack triggers
│       │   ├── SecurityAlerts.jsx     # Incident triage & severity filters
│       │   ├── PrivacyCenter.jsx      # Zero-trust privacy & pseudonym management
│       │   ├── Analytics.jsx          # Traffic density & threat breakdowns
│       │   ├── Evaluation.jsx         # Autonomous benchmark & Confusion Matrix
│       │   └── Settings.jsx           # Detection limits & TTL configuration
│       ├── services/
│       │   ├── api.js                 # Central fetch client
│       │   └── dashboardService.js    # Multi-endpoint data consolidator
│       └── utils/
│           ├── constants.js           # Severity palettes & event mappings
│           └── formatters.js          # IPv6 and UTC date formatters
│
├── docs/
│   ├── architecture.md                # Component architecture & security layers
│   ├── API_DOCUMENTATION.md           # REST API specification & schemas
│   ├── TESTING_GUIDE.md               # 20-test automated verification guide
│   ├── DEMONSTRATION_GUIDE.md         # 5-minute hackathon presentation script
│   └── LIMITATIONS.md                 # Assumptions, bounds & privacy disclosures
│
└── scripts/
    ├── seed_demo_data.py              # Populates SQLite with baseline devices
    ├── run_backend.py                 # Launches standalone Flask backend
    ├── run_evaluation.py              # Standalone benchmark evaluation runner
    └── export_project_zip.py          # Builds standalone repository archive
```

---

## 4. Windows Installation and Execution (PowerShell)

### Prerequisites Check
Open **Windows PowerShell** (or Windows Terminal) and verify your tools:
```powershell
# 1. Verify Python version (Python 3.10 or 3.11 recommended)
python --version
# Or using the Windows Python launcher:
py --version

# 2. Verify Node.js and npm
node --version
npm --version
```

### Step 1: Clone / Extract Project
```powershell
cd C:\Projects
# If extracted from ZIP:
cd PrivacyGuard-IPv6
```

### Step 2: Configure Python Virtual Environment
*(Note: If PowerShell execution policy restricts scripts, bypass it safely for the current process)*
```powershell
# Create virtual environment
python -m venv venv

# Bypass execution policy for current PowerShell session and activate:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# Alternative (direct execution without activating script):
# & .\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 3: Install Backend Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Initialise and Seed SQLite Database
```powershell
python scripts\seed_demo_data.py
```
*Expected Output:*
```text
============================================================
PrivacyGuard IPv6 - Database Initialisation & Seeding
============================================================
[+] Provisioned 2 Tenants:
    - tenant-alpha: Tenant Alpha (Smart Facility A)
    - tenant-beta: Tenant Beta (Smart Logistics B)
[+] Provisioned Devices:
    - Tenant tenant-alpha: 5 active IoT devices
    - Tenant tenant-beta: 5 active IoT devices
[+] Initial Cryptographic Pseudonyms: 10
Database seeded successfully. Ready for demonstration!
```

### Step 5: Install Frontend Dependencies
```powershell
npm install
```

---

## 5. Starting the System

### Option A: Full-Stack Mode (Single Command)
Starts the unified Express full-stack server on port 3000 (proxies `/api/*` to the Python/SQLite engine and serves Vite hot-reload frontend):
```powershell
npm run dev
```
Open your browser to: **`http://localhost:3000`**

### Option B: Decoupled Independent Mode (Two Terminals)

**Terminal 1 (Flask REST API):**
```powershell
.\venv\Scripts\Activate.ps1
python scripts\run_backend.py
# Backend runs on http://127.0.0.1:5000
```
Verify the health check in your browser or PowerShell:
```powershell
curl http://127.0.0.1:5000/api/health
```

**Terminal 2 (React Vite Frontend):**
```powershell
npm run dev
# Frontend runs on http://localhost:3000
```

---

## 6. How to Run Automated Tests

The test suite covers all 16 specification requirements (20 total tests).

### Using Pytest:
```powershell
pytest -q
```

### Using Python Standard `unittest` (Zero External Dependencies):
```powershell
python -m unittest discover backend/tests -v
```

*Expected Test Output:*
```text
test_summary_and_traffic_aggregation (test_analytics.TestAnalytics) ... ok
test_five_devices_initialised (test_devices.TestDevices) ... ok
test_temporary_address_rotation (test_devices.TestDevices) ... ok
test_api_validation (test_evaluation.TestEvaluation) ... ok
test_evaluation_metric_calculation (test_evaluation.TestEvaluation) ... ok
test_reset_demonstration (test_evaluation.TestEvaluation) ... ok
test_zero_denominator_safety (test_evaluation.TestEvaluation) ... ok
test_abnormal_ndp_rate (test_ndp_anomaly.TestNDPAnomaly) ... ok
test_normal_ndp_rate (test_ndp_anomaly.TestNDPAnomaly) ... ok
test_manual_pseudonym_revocation (test_pseudonyms.TestPseudonyms) ... ok
test_pseudonym_expiration_rejection (test_pseudonyms.TestPseudonyms) ... ok
test_pseudonym_generation_and_active_validation (test_pseudonyms.TestPseudonyms) ... ok
test_legitimate_router_advertisement (test_rogue_ra.TestRogueRA) ... ok
test_rogue_ra_hijacked_prefix_from_trusted_source (test_rogue_ra.TestRogueRA) ... ok
test_rogue_router_advertisement_unauthorised_source (test_rogue_ra.TestRogueRA) ... ok
test_session_creation_and_bearer_validation (test_sessions.TestSessions) ... ok
test_session_expiration (test_sessions.TestSessions) ... ok
test_session_revocation (test_sessions.TestSessions) ... ok
test_rate_counter_isolation (test_tenant_isolation.TestTenantIsolation) ... ok
test_tenant_data_isolation (test_tenant_isolation.TestTenantIsolation) ... ok

----------------------------------------------------------------------
Ran 20 tests in 2.494s

OK
```

---

## 7. Autonomous Security Evaluation Suite

Run the evaluation script via CLI:
```powershell
python scripts\run_evaluation.py
```
Or click the **"Run Evaluation Suite"** button on the **Evaluation** page in the dashboard.

### Confusion Matrix & Formulas

- **True Positives (TP):** Attack vectors correctly flagged (Rogue RAs, NDP flood bursts).
- **False Positives (FP):** Normal cases incorrectly flagged as attacks (Legitimate RAs, SLAAC address rotations).
- **True Negatives (TN):** Normal cases correctly accepted.
- **False Negatives (FN):** Attack cases that bypassed detection.

$$\text{Detection Rate (Recall)} = \frac{\text{TP}}{\text{TP} + \text{FN}} \times 100\%$$

$$\text{False-Positive Rate (FPR)} = \frac{\text{FP}}{\text{FP} + \text{TN}} \times 100\%$$

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} \times 100\%$$

$$\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

*Zero-Denominator Guard:* If $\text{TP} + \text{FN} = 0$ or $\text{Precision} + \text{Recall} = 0$, the engine safely returns `0.0%` rather than throwing an unhandled exception.

---

## 8. Hackathon Demonstration Sequence

Follow this sequence for the AIORI 3 Hackathon presentation:

1. **Dashboard Overview:** Open `http://localhost:3000`. Show the live SOC header, the 5 IoT nodes, and zero hardcoded metrics.
2. **Device Fleet & Privacy Address Rotation:**
   - Go to **Devices**. View the 5 devices with RFC 4941 IPv6 addresses and pseudonyms.
   - Click **"Rotate IP"** on Node 1: watch the address rotate and fresh pseudonym generate.
   - Go to **Security Alerts**: prove **no false alarm** was created.
3. **Simulate Rogue Router Advertisement:**
   - In the sidebar, click **"Simulate Rogue RA"**.
   - An unauthorized router (`fe80::dead:beef:666`) injects an evil prefix.
   - The detector flags a **CRITICAL** alert in the **Security Alerts** table. Click **"Acknowledge"** to show SOC triage.
4. **Simulate NDP Anomaly:**
   - Click **"Simulate NDP Anomaly"**.
   - A burst of 55 Neighbor Solicitations triggers the sliding-window detector.
   - A **HIGH** severity **NDP_ANOMALY** alert is logged.
5. **Privacy Center & Expiration Rejection:**
   - Open **Privacy Center**. Show active pseudonyms and hashed sessions (no plaintext tokens).
   - Click **"Expire / Revoke"** on an active pseudonym. The state switches to `EXPIRED`. Subsequent packets are rejected with HTTP 401.
6. **Multi-Tenant Isolation:**
   - Switch tenant from `Tenant Alpha` to `Tenant Beta` in the top header.
   - Show that Tenant Beta has independent devices (`2001:db8:2::/64`) and zero visibility into Tenant Alpha's incidents.
7. **Run Benchmark Evaluation:**
   - Open **Evaluation** and click **"Run Evaluation Suite"**.
   - Point out the 8 ground-truth vectors, Confusion Matrix, 100% Recall, and 0% FPR.
8. **Export & Reset:**
   - Click **"Export ZIP"** in the top bar to download the complete archive.
   - Click **"Reset Demo State"** to restore pristine baseline status.

---

## 9. Security & Privacy Disclosure

- **Software Simulation:** The baseline core uses Python simulation without physical network adapters or root permissions.
- **Anonymity Boundaries:** Ephemeral pseudonyms eliminate permanent MAC and static IPv6 EUI-64 tracking in application telemetry. Physical-layer RF fingerprinting or raw switch port correlation remains possible on unmanaged physical links.
- **Passive NIDS:** The application functions as a passive monitoring and alerting system. It does not manipulate switch ACLs or drop traffic inline.

---

## 10. License

Developed for the **AIORI 3 Hackathon** (PS-007). Provided under the MIT License for educational and research evaluation.
