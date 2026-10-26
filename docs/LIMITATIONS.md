# PrivacyGuard IPv6 — Security Assumptions and System Limitations

This document provides transparent disclosure regarding security bounds, privacy guarantees, and architectural trade-offs in PrivacyGuard IPv6.

---

## 1. Simulation Environment vs. Physical Network Tap

- **Software Simulation Baseline:** The core release functions via software-simulated IPv6 events generated programmatically using SQLite and Python. This ensures 100% reproducibility on standard developer workstations without requiring physical IoT sensors, managed IPv6 routers, or root/raw socket privileges.
- **Optional Scapy Live Capture:** An optional Scapy module can bind to live network interfaces (e.g. `eth0`, `wlan0`), but requires OS administrative privileges (`CAP_NET_RAW` on Linux or Npcap on Windows) and promiscuous mode support on the physical network adapter.

---

## 2. Privacy Scope & Anonymity Boundaries

- **Local Link Pseudonymization:** The pseudonymization mechanism eliminates persistent device identifiers (such as IEEE MAC addresses or EUI-64 tokens) from application-level telemetry and monitoring dashboards.
- **No Absolute Anonymity Claim:** While local pseudonyms prevent application-level tracking across sessions and tenants, external network observers with full packet inspection capabilities on the physical link may still correlate traffic through physical-layer metadata (e.g., radio-frequency fingerprinting, packet timing analysis, packet size clustering, or physical switch port numbers).
- **Tenant Scope:** Pseudonym entropy (16 bits) is intentionally lightweight for IoT microcontroller telemetry headers (`DEV-XXXX`). For larger enterprise fleets, pseudonym entropy can be expanded to 64 or 128 bits.

---

## 3. Threat Detection Assumptions

- **Rogue Router Advertisements:** The RA detector depends on a configured whitelist of trusted default routers and permitted IPv6 subnet prefixes. If an adversary compromises a legitimately authorized router's private key or IP address (e.g., link-local spoofing without SEND / SeND RFC 3971), cryptographic RA signatures (such as SeND CGA) are required for link-layer cryptographic proof.
- **NDP Rate Anomaly Detection:** The sliding-window rate counter detects volumetric flooding (e.g. DoS cache-exhaustion). Low-and-slow stealth attacks that operate beneath the configured threshold (e.g., 1 solicitation every 15 seconds) will not trigger the volumetric threshold detector.
- **Non-Inline Blocking:** By default, PrivacyGuard IPv6 operates as a **passive monitoring and alerting system (NIDS)**. It does not inject ICMPv6 RA Guard drops or firewall drop rules unless integrated with an SDN controller (e.g., OpenFlow/OVS) or hardware switch ACLs.
