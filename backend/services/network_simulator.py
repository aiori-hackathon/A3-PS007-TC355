"""
Network Simulator Service
Simulates five IPv6 IoT devices per tenant with SLAAC address rotation,
Router Advertisements, and Neighbor Discovery Protocol (NDP) interactions.
Provides test-scenario generators for normal traffic, Rogue RAs, and NDP rate anomalies.
"""
import random
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, List

from backend.services.ipv6_address_service import IPv6AddressService
from backend.services.pseudonym_service import PseudonymService
from backend.services.session_service import SessionService
from backend.services.event_processor import EventProcessor

class NetworkSimulator:
    def __init__(self, event_processor: EventProcessor = None):
        self.processor = event_processor or EventProcessor()

    def generate_normal_traffic(self, conn, tenant_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generates legitimate NDP / telemetry traffic from active devices."""
        cur = conn.cursor()
        cur.execute("""
        SELECT device_id, device_name, current_ipv6, current_pseudonym
        FROM devices
        WHERE tenant_id = ? AND status = 'CONNECTED'
        """, (tenant_id,))
        devices = cur.fetchall()

        if not devices:
            return []

        results = []
        for _ in range(count):
            dev = random.choice(devices)
            pseudo = dev["current_pseudonym"]
            # Ensure pseudonym is active
            val_p = PseudonymService.validate_pseudonym(conn, pseudo, tenant_id)
            if not val_p["valid"]:
                new_p = PseudonymService.create_pseudonym(conn, tenant_id, lifetime_seconds=1800, device_ref=dev["device_id"])
                pseudo = new_p["pseudonym"]
                cur.execute("UPDATE devices SET current_pseudonym = ? WHERE device_id = ? AND tenant_id = ?", (pseudo, dev["device_id"], tenant_id))
                conn.commit()

            msg_type = random.choice(["NEIGHBOR_SOLICITATION", "NEIGHBOR_ADVERTISEMENT", "NDP_MESSAGE"])
            evt_data = {
                "tenant_id": tenant_id,
                "event_type": msg_type,
                "pseudonym": pseudo,
                "source_ipv6": dev["current_ipv6"],
                "payload": {
                    "device_name": dev["device_name"],
                    "hop_limit": 255,
                    "target_address": "fe80::1",
                    "code": 0
                }
            }
            res = self.processor.process_event(conn, evt_data)
            results.append(res)

        # Include an authorised Router Advertisement from trusted default gateway
        legit_ra = {
            "tenant_id": tenant_id,
            "event_type": "ROUTER_ADVERTISEMENT",
            "source_ipv6": "fe80::1",
            "router_id": "fe80::1",
            "advertised_prefix": "2001:db8:1::/64" if tenant_id == "tenant-alpha" else "2001:db8:2::/64",
            "router_lifetime": 1800,
            "payload": {
                "flags": {"managed": False, "other": False},
                "cur_hop_limit": 64,
                "reachable_time": 30000,
                "retrans_timer": 1000
            }
        }
        res_ra = self.processor.process_event(conn, legit_ra)
        results.append(res_ra)
        return results

    def simulate_rogue_ra(
        self,
        conn,
        tenant_id: str,
        unauthorized_source: str = "fe80::dead:beef:666",
        bogus_prefix: str = "2001:db8:malicious::/64"
    ) -> Dict[str, Any]:
        """
        Simulates an attacker injecting an unauthorised ICMPv6 Router Advertisement message
        to poison default gateways or hijack IPv6 prefixes.
        """
        evt_data = {
            "tenant_id": tenant_id,
            "event_type": "ROGUE_RA",
            "source_ipv6": unauthorized_source,
            "router_id": unauthorized_source,
            "advertised_prefix": bogus_prefix,
            "router_lifetime": 1800,
            "payload": {
                "attack_vector": "Rogue IPv6 Gateway Advertisement",
                "attempted_prefix_hijack": bogus_prefix,
                "rogue_mac": "02:00:5e:66:de:ad",
                "flags": {"managed": True, "other": True}
            }
        }
        return self.processor.process_event(conn, evt_data)

    def simulate_ndp_anomaly(
        self,
        conn,
        tenant_id: str,
        burst_count: int = 55,
        target_pseudonym: str = None
    ) -> Dict[str, Any]:
        """
        Simulates an abnormal burst of Neighbour Solicitation / Advertisement frames
        aimed at table-exhaustion / DoS.
        """
        cur = conn.cursor()
        dev_id = None
        if not target_pseudonym:
            cur.execute("SELECT device_id, current_pseudonym, current_ipv6 FROM devices WHERE tenant_id = ? AND status = 'CONNECTED' LIMIT 1", (tenant_id,))
            row = cur.fetchone()
            if not row:
                cur.execute("SELECT device_id, current_pseudonym, current_ipv6 FROM devices WHERE tenant_id = ? LIMIT 1", (tenant_id,))
                row = cur.fetchone()
            if row:
                dev_id = row["device_id"]
                target_pseudonym = row["current_pseudonym"]
                source_ipv6 = row["current_ipv6"]
            else:
                p_new = PseudonymService.create_pseudonym(conn, tenant_id, lifetime_seconds=1800)
                target_pseudonym = p_new["pseudonym"]
                source_ipv6 = "2001:db8:1::99"
        else:
            cur.execute("SELECT device_id, current_ipv6 FROM devices WHERE current_pseudonym = ? AND tenant_id = ?", (target_pseudonym, tenant_id))
            row = cur.fetchone()
            if row:
                dev_id = row["device_id"]
                source_ipv6 = row["current_ipv6"]
            else:
                source_ipv6 = "2001:db8:1::99"

        # Ensure the pseudonym is active; if expired, refresh it for this simulated node
        val_check = PseudonymService.validate_pseudonym(conn, target_pseudonym, tenant_id)
        if not val_check["valid"]:
            new_pseudo_obj = PseudonymService.create_pseudonym(conn, tenant_id, lifetime_seconds=1800, device_ref=dev_id)
            target_pseudonym = new_pseudo_obj["pseudonym"]
            if dev_id:
                cur.execute("UPDATE devices SET current_pseudonym = ? WHERE device_id = ? AND tenant_id = ?", (target_pseudonym, dev_id, tenant_id))
                conn.commit()

        last_result = None
        alert_triggered_result = None
        for i in range(burst_count):
            evt_data = {
                "tenant_id": tenant_id,
                "event_type": "NEIGHBOR_SOLICITATION",
                "pseudonym": target_pseudonym,
                "source_ipv6": source_ipv6,
                "payload": {
                    "seq": i + 1,
                    "target_solicited": f"2001:db8:1::{i:x}",
                    "is_burst": True
                }
            }
            res = self.processor.process_event(conn, evt_data)
            if res.get("alert_created"):
                alert_triggered_result = res
            last_result = res

        return alert_triggered_result or last_result

    def rotate_device_address(self, conn, device_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Executes an RFC 4941 privacy temporary address rotation for a simulated device.
        Ensures that rotation does NOT trigger attack alerts.
        """
        cur = conn.cursor()
        cur.execute("SELECT device_id, current_ipv6, current_pseudonym, device_name FROM devices WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
        dev = cur.fetchone()
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found in tenant {tenant_id}"}

        old_ip = dev["current_ipv6"]
        new_ip = IPv6AddressService.rotate_address(old_ip, tenant_id)
        
        # Also refresh pseudonym to demonstrate ephemeral privacy rotation
        new_pseudo_data = PseudonymService.create_pseudonym(conn, tenant_id, lifetime_seconds=300, device_ref=device_id)
        new_pseudo = new_pseudo_data["pseudonym"]

        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("""
        UPDATE devices
        SET current_ipv6 = ?, current_pseudonym = ?, last_event_at = ?
        WHERE device_id = ? AND tenant_id = ?
        """, (new_ip, new_pseudo, now_iso, device_id, tenant_id))

        # Log IPV6_ADDRESS_ROTATED event - this must NOT be marked suspicious
        evt_data = {
            "tenant_id": tenant_id,
            "event_type": "IPV6_ADDRESS_ROTATED",
            "pseudonym": new_pseudo,
            "source_ipv6": new_ip,
            "payload": {
                "previous_ipv6": old_ip,
                "new_ipv6": new_ip,
                "privacy_standard": "RFC 4941",
                "note": "Routine temporary privacy address rotation"
            }
        }
        res = self.processor.process_event(conn, evt_data)

        return {
            "success": True,
            "device_id": device_id,
            "previous_ipv6": old_ip,
            "new_ipv6": new_ip,
            "new_pseudonym": new_pseudo,
            "event_result": res
        }
