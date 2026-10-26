"""
Rogue Router Advertisement (RA) Detector
Analyzes ICMPv6 Type 134 (Router Advertisement) messages against trusted router registries
and permitted prefix policies.
"""
from typing import Dict, Any, Optional
from backend.config import Config

class RADetector:
    def __init__(self, trusted_routers=None, allowed_prefixes=None):
        self.trusted_routers = set(trusted_routers or Config.TRUSTED_ROUTERS)
        self.allowed_prefixes = set(allowed_prefixes or Config.ALLOWED_PREFIXES)

    def evaluate_ra(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a simulated ICMPv6 Router Advertisement event.
        Returns:
            {
                "is_rogue": bool,
                "severity": "CRITICAL" | "HIGH" | "NONE",
                "reason": str,
                "evidence": dict
            }
        """
        source_ip = event_data.get("source_ipv6", "")
        router_id = event_data.get("router_id", source_ip)
        advertised_prefix = event_data.get("advertised_prefix", "")
        router_lifetime = event_data.get("router_lifetime", 1800)

        evidence = {
            "source_ip": source_ip,
            "router_id": router_id,
            "advertised_prefix": advertised_prefix,
            "router_lifetime": router_lifetime,
            "trusted_routers": list(self.trusted_routers),
            "allowed_prefixes": list(self.allowed_prefixes)
        }

        # Check 1: Unauthorised router source
        is_trusted_router = (source_ip in self.trusted_routers) or (router_id in self.trusted_routers)
        if not is_trusted_router:
            return {
                "is_rogue": True,
                "severity": "CRITICAL",
                "category": "ROGUE_RA",
                "reason": f"Unauthorised ICMPv6 Router Advertisement source [{source_ip or router_id}] not in trusted router list.",
                "evidence": evidence
            }

        # Check 2: Unauthorised or hijack prefix advertised by router
        if advertised_prefix and advertised_prefix not in self.allowed_prefixes:
            return {
                "is_rogue": True,
                "severity": "HIGH",
                "category": "ROGUE_RA",
                "reason": f"Authorised router [{router_id}] advertised unauthorised prefix [{advertised_prefix}].",
                "evidence": evidence
            }

        # Check 3: Malicious zero-lifetime blackhole attempt
        if router_lifetime == 0 and event_data.get("is_revocation_attack", False):
            return {
                "is_rogue": True,
                "severity": "HIGH",
                "category": "ROGUE_RA",
                "reason": f"Suspicious RA zero-lifetime default router withdrawal received.",
                "evidence": evidence
            }

        # Normal, authorised Router Advertisement
        return {
            "is_rogue": False,
            "severity": "NONE",
            "category": "NORMAL_RA",
            "reason": f"Authorised RA from trusted source [{router_id}] with permitted prefix [{advertised_prefix}].",
            "evidence": evidence
        }
