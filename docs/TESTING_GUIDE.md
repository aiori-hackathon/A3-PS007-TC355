# PrivacyGuard IPv6 — Automated Testing Guide

This guide describes how to run and interpret the automated test suite for PrivacyGuard IPv6.

---

## 1. Quick Test Execution

### Windows (PowerShell)
```powershell
# In project root with active venv:
pytest -q
```
Or using Python's built-in test runner (zero external dependencies):
```powershell
python -m unittest discover backend/tests -v
```

### Linux / macOS / AI Studio
```bash
python3 -m unittest discover backend/tests -v
```

---

## 2. Test Suite Overview

| Test Case | Module | Description | Acceptance Criteria Verified |
|---|---|---|---|
| **TEST 1** | `test_devices.py` | Device Initialisation | Exactly 5 IoT devices are provisioned per tenant with valid IPv6 prefixes and pseudonyms. |
| **TEST 2** | `test_rogue_ra.py` | Legitimate Router Advertisement | Authorised RA from trusted source advertising allowed prefix does NOT trigger alerts. |
| **TEST 3** | `test_rogue_ra.py` | Rogue Router Advertisement | Unauthorised router injecting an RA triggers a **CRITICAL** Rogue RA alert. |
| **TEST 4** | `test_ndp_anomaly.py` | Abnormal NDP Rate Detection | Rapid burst of Neighbor Solicitations exceeding the threshold triggers an **NDP_ANOMALY** alert. |
| **TEST 5** | `test_ndp_anomaly.py` | Normal NDP Message Rate | Traffic volume below configured rate threshold is accepted without false alarms. |
| **TEST 6** | `test_devices.py` | SLAAC Address Rotation | RFC 4941 address rotation generates new suffix and pseudonym without generating security alerts. |
| **TEST 7** | `test_pseudonyms.py` | Pseudonym Expiration Enforcement | Expired pseudonyms are strictly rejected for subsequent event submissions. |
| **TEST 8** | `test_sessions.py` | Session Expiration Enforcement | Expired sessions cannot submit telemetry events. |
| **TEST 9** | `test_sessions.py` | Session Revocation | Revoked sessions are immediately invalidated and cannot be reused. |
| **TEST 10** | `test_tenant_isolation.py` | Cross-Tenant Data Isolation | Tenant Alpha cannot query or correlate Tenant Beta devices, sessions, or alerts. |
| **TEST 11** | `test_tenant_isolation.py` | Rate-Counter Isolation | NDP rate counters for identical pseudonym names are strictly partitioned per tenant. |
| **TEST 12** | `test_evaluation.py` | Metric Calculation | True Positives, False Positives, Recall, Precision, and F1 are computed from ground-truth test vectors. |
| **TEST 13** | `test_evaluation.py` | Zero-Denominator Safety | Dividing by zero in edge cases produces 0.0 without runtime exceptions. |
| **TEST 14** | `test_evaluation.py` | API Boundary Validation | Invalid configuration bounds (negative thresholds) and malformed requests return HTTP 400. |
| **TEST 15** | `test_evaluation.py` | Reset Demonstration | Environment can be reset safely, restoring clean initial state and clearing junk records. |
| **TEST 16** | `test_pseudonyms.py` | Privacy Revocation Audit | Immediate revocation invalidates pseudonym in database and flags audit status. |

---

## 3. Interpreting Test Results

When executed, a healthy test suite will conclude with:

```text
----------------------------------------------------------------------
Ran 20 tests in 2.494s

OK
```

If any test fails, Pytest / unittest displays the exact line number, assertion diff, and operational failure reason.
