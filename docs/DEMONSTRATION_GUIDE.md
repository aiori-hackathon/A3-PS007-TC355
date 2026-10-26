# PrivacyGuard IPv6 — Hackathon Demonstration Guide

**Event:** AIORI 3 Hackathon  
**Problem Statement:** PS-007: Privacy-Aware IPv6 IoT Security Monitoring  

Follow this chronological presentation script for an impactful 5-minute hackathon demo.

---

## Step 1: Open the SOC Dashboard Overview
1. Navigate to the **Dashboard** page (`http://localhost:3000`).
2. Point out:
   - **Backend Status:** Connected to SQLite & Flask API.
   - **Active Tenant Selector:** Tenant Alpha vs. Tenant Beta.
   - **5 Simulated IoT Devices:** Connected in documentation subnet `2001:db8:1::/64`.
   - **Zero Hardcoded Numbers:** All KPI stat cards and charts are live queries.

---

## Step 2: Show the 5 Simulated IPv6 IoT Devices & Address Rotation
1. Navigate to the **Devices** page.
2. View the 5 devices:
   - Temperature Sensor (`dev-alpha-01`)
   - Smart Lighting Controller (`dev-alpha-02`)
   - Environmental Sensor (`dev-alpha-03`)
   - Smart Gateway (`dev-alpha-04`)
   - Security Sensor (`dev-alpha-05`)
3. Note that each device uses a temporary IPv6 address and an ephemeral pseudonym (e.g. `DEV-B3E9`).
4. Click **"Rotate Address"** on the Temperature Sensor:
   - Observe the IPv6 address update to a new random interface identifier.
   - Notice that a new temporary pseudonym is issued.
   - Switch to the **Security Alerts** page: point out that **no false alert was triggered** (RFC 4941 compliance).

---

## Step 3: Trigger a Rogue Router Advertisement (RA) Attack
1. Navigate to **Live Monitoring**.
2. Click **"Simulate Rogue RA"**:
   - The simulator injects an ICMPv6 Type 134 packet from unauthorised router `fe80::dead:beef:666` advertising an evil prefix `2001:db8:evil::/64`.
3. Notification popup confirms detection.
4. Navigate to **Security Alerts**:
   - A **CRITICAL** alert appears immediately:
     *"Unauthorised ICMPv6 Router Advertisement source [fe80::dead:beef:666] not in trusted router list."*
   - Click **"Acknowledge"** to show SOC incident management audit logging.

---

## Step 4: Trigger an NDP Burst Rate Anomaly
1. On **Live Monitoring**, click **"Simulate NDP Anomaly"**:
   - The simulator generates a flood of 55 Neighbor Solicitation messages within a 10-second window.
2. The sliding-window rate detector flags the burst exceeding the 50 msg threshold.
3. A **HIGH** severity **NDP_ANOMALY** alert is created with exact rate evidence.

---

## Step 5: Demonstrate Privacy Center & Expiration Rejection
1. Open the **Privacy Center** page:
   - Inspect active pseudonyms and short-lived sessions.
   - Note that **plaintext bearer tokens and permanent MAC addresses are never stored or exposed**.
2. Click **"Expire / Revoke"** on one of the active pseudonyms.
3. Observe its status immediately switch to **EXPIRED**.
4. Highlight that any subsequent network event bearing this expired pseudonym will be rejected with HTTP 401.

---

## Step 6: Verify Multi-Tenant Cryptographic Isolation
1. In the header bar, switch tenant to **Tenant Beta (Smart Logistics B)**.
2. Show that:
   - Tenant Beta has its own distinct device fleet (`2001:db8:2::/64`).
   - Tenant Alpha's alerts and events are completely absent from Tenant Beta's view.
   - Cross-tenant correlation is impossible.

---

## Step 7: Run the Autonomous Evaluation Benchmark
1. Navigate to the **Evaluation** page.
2. Click **"Run Evaluation"**:
   - The benchmark executes 8 ground-truth test vectors (3 Rogue RA attacks, 2 legitimate RAs, 1 SLAAC address rotation, 1 NDP flood attack, and 1 normal NDP exchange).
3. The live Confusion Matrix renders:
   - **True Positives (TP):** 4
   - **False Positives (FP):** 0
   - **True Negatives (TN):** 4
   - **False Negatives (FN):** 0
   - **Detection Rate (Recall):** 100.0%
   - **False-Positive Rate:** 0.0%
   - **Precision:** 100.0%
   - **F1 Score:** 100.0%
4. Conclude by demonstrating **"Reset Demo"** on the dashboard to return the environment to a pristine initial state.
