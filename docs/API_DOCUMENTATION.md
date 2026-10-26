# PrivacyGuard IPv6 — REST API Documentation

Base URL: `http://localhost:5000/api` (or proxied via frontend)  
Content-Type: `application/json`

---

## 1. General & Dashboard

### `GET /api/health`
Checks backend and SQLite connection status.
- **Response `200`:**
  ```json
  {
    "status": "healthy",
    "service": "PrivacyGuard IPv6",
    "version": "1.0.0",
    "backend": "Flask",
    "database": "SQLite"
  }
  ```

### `GET /api/dashboard?tenant_id=tenant-alpha`
Returns high-level SOC dashboard stats, monitoring state, recent alerts, and events.
- **Parameters:** `tenant_id` (default: `tenant-alpha`)
- **Response `200`:**
  ```json
  {
    "success": true,
    "tenant_id": "tenant-alpha",
    "summary": {
      "total_devices": 5,
      "total_events": 48,
      "total_alerts": 3,
      "rogue_ra_alerts": 1,
      "ndp_alerts": 2,
      "active_pseudonyms": 5,
      "expired_pseudonyms": 1,
      "active_sessions": 5
    },
    "monitoring_active": true,
    "recent_alerts": [...],
    "recent_events": [...]
  }
  ```

---

## 2. Simulated IoT Devices

### `GET /api/devices?tenant_id=tenant-alpha`
Lists all five simulated IoT devices for the tenant.

### `GET /api/devices/<device_id>/events?tenant_id=tenant-alpha`
Returns recent network events associated with the device's pseudonym.

### `POST /api/devices/<device_id>/rotate-address`
Rotates the device's SLAAC IPv6 interface identifier and generates a fresh ephemeral pseudonym.
- **Payload:** `{"tenant_id": "tenant-alpha"}`
- **Response `200`:**
  ```json
  {
    "success": true,
    "device_id": "dev-alpha-01",
    "previous_ipv6": "2001:db8:1::1:10a4:bc89",
    "new_ipv6": "2001:db8:1::1:90ef:31ca",
    "new_pseudonym": "DEV-49F1"
  }
  ```

### `POST /api/devices/<device_id>/connect`
Sets device status to `CONNECTED`.

### `POST /api/devices/<device_id>/disconnect`
Sets device status to `DISCONNECTED`.

---

## 3. Monitoring Control

### `GET /api/monitoring/status?tenant_id=tenant-alpha`
Returns current live monitoring engine status and event counts.

### `POST /api/monitoring/start`
Resumes live network event processing.

### `POST /api/monitoring/stop`
Pauses live network event processing.

---

## 4. Threat Simulation & Testing

### `POST /api/simulation/normal-traffic`
Generates legitimate NDP exchanges and authorised Router Advertisements.
- **Payload:** `{"tenant_id": "tenant-alpha", "count": 5}`

### `POST /api/simulation/rogue-ra`
Simulates an unauthorised ICMPv6 Router Advertisement injection.
- **Payload:** `{"tenant_id": "tenant-alpha", "source_ipv6": "fe80::dead:beef:666", "advertised_prefix": "2001:db8:evil::/64"}`
- **Response `200`:**
  ```json
  {
    "success": true,
    "message": "Simulated Rogue Router Advertisement injected",
    "alert_generated": true,
    "alert_id": "alt_e1289a",
    "detection": {
      "category": "ROGUE_RA",
      "severity": "CRITICAL",
      "reason": "Unauthorised ICMPv6 Router Advertisement source [fe80::dead:beef:666] not in trusted router list."
    }
  }
  ```

### `POST /api/simulation/ndp-anomaly`
Simulates an abnormal burst of Neighbor Solicitation messages exceeding the threshold.
- **Payload:** `{"tenant_id": "tenant-alpha", "burst_count": 55}`

### `POST /api/simulation/reset`
Resets the demonstration environment by clearing events and alerts and reseeding 5 clean devices per tenant.

---

## 5. Security Alerts

### `GET /api/alerts?tenant_id=tenant-alpha&severity=CRITICAL&category=ROGUE_RA`
Lists alerts filtered by tenant, severity, and category.

### `POST /api/alerts/<alert_id>/acknowledge`
Acknowledges an alert with SOC analyst audit record.
- **Payload:** `{"tenant_id": "tenant-alpha", "analyst": "SOC-Lead"}`

---

## 6. Privacy & Session Management

### `GET /api/privacy/status?tenant_id=tenant-alpha`
Returns counts of active vs expired pseudonyms and sessions.

### `GET /api/privacy/pseudonyms?tenant_id=tenant-alpha`
Lists all pseudonyms, expiration timestamps, and revocation status.

### `POST /api/privacy/pseudonyms/expire`
Revokes/expires a pseudonym immediately.
- **Payload:** `{"tenant_id": "tenant-alpha", "pseudonym": "DEV-A81F"}`

### `GET /api/privacy/sessions?tenant_id=tenant-alpha`
Lists active/expired sessions without exposing bearer tokens.

### `POST /api/privacy/sessions/revoke`
Revokes a monitoring session token.
- **Payload:** `{"tenant_id": "tenant-alpha", "session_id": "sess_81fc20..."}`

---

## 7. Analytics & Evaluation

### `GET /api/analytics/traffic?tenant_id=tenant-alpha`
Returns traffic breakdown by event type and time series.

### `GET /api/analytics/alerts?tenant_id=tenant-alpha`
Returns alert distribution by severity and threat category.

### `POST /api/evaluation/run`
Executes ground-truth benchmark suite and returns confusion matrix and metrics.

### `GET /api/evaluation/results`
Retrieves latest benchmark evaluation results.

---

## 8. Configuration Settings

### `GET /api/settings`
Returns operational thresholds (NDP limit, sliding window, pseudonym TTL, session TTL).

### `PUT /api/settings`
Updates operational thresholds with strict bounds validation.
- **Payload:**
  ```json
  {
    "ndp_threshold": 60,
    "ndp_window_seconds": 15,
    "pseudonym_lifetime_seconds": 300,
    "session_lifetime_seconds": 180,
    "event_retention_days": 14
  }
  ```
