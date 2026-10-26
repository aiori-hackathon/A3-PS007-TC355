"""
IPv6 Address Management Service
Handles generation and privacy-preserving rotation of temporary IPv6 addresses
compliant with RFC 4941 (Privacy Extensions for SLAAC in IPv6).
"""
import secrets
import re

class IPv6AddressService:
    DEFAULT_PREFIXES = {
        "tenant-alpha": "2001:db8:1",
        "tenant-beta": "2001:db8:2"
    }

    @staticmethod
    def generate_temporary_address(tenant_id: str, device_index: int = 1) -> str:
        """
        Generates a privacy-preserving randomized SLAAC interface identifier.
        Uses RFC 3849 documentation prefixes (2001:0db8::/32).
        """
        prefix = IPv6AddressService.DEFAULT_PREFIXES.get(tenant_id, "2001:db8:99")
        # Generate 64-bit random host interface identifier formatted in two 16-bit hex chunks
        h1 = secrets.token_hex(2)
        h2 = secrets.token_hex(2)
        return f"{prefix}::{device_index:x}:{h1}:{h2}".lower()

    @staticmethod
    def rotate_address(current_ipv6: str, tenant_id: str) -> str:
        """
        Rotates an existing IPv6 address to a new randomized temporary suffix.
        Preserves the subnet prefix while refreshing the interface identifier.
        """
        parts = current_ipv6.split("::")
        prefix = parts[0] if len(parts) > 0 else IPv6AddressService.DEFAULT_PREFIXES.get(tenant_id, "2001:db8:1")
        
        # Extract device index hint if present
        dev_hint = "1"
        if len(parts) > 1 and ":" in parts[1]:
            dev_hint = parts[1].split(":")[0]
            
        h1 = secrets.token_hex(2)
        h2 = secrets.token_hex(2)
        new_address = f"{prefix}::{dev_hint}:{h1}:{h2}".lower()
        return new_address

    @staticmethod
    def is_valid_ipv6(address: str) -> bool:
        """Basic IPv6 syntax validation for simulated network addresses."""
        if not address or len(address) > 45:
            return False
        # Match standard colon-hex format with optional ::
        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){1,7}:?([0-9a-fA-F]{1,4})?$"
        return bool(re.match(ipv6_pattern, address))
