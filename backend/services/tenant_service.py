"""
Tenant Isolation Service
Enforces strict boundaries between tenant contexts (Tenant Alpha vs Tenant Beta).
"""
from typing import List, Dict, Any, Optional

class TenantService:
    @staticmethod
    def get_tenants(conn) -> List[Dict[str, Any]]:
        cur = conn.cursor()
        cur.execute("SELECT tenant_id, name, created_at FROM tenants ORDER BY tenant_id ASC")
        return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def is_valid_tenant(conn, tenant_id: str) -> bool:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM tenants WHERE tenant_id = ?", (tenant_id,))
        return cur.fetchone() is not None

    @staticmethod
    def verify_access(conn, tenant_id: str, resource_tenant_id: str) -> bool:
        """Confirms that a requested resource belongs strictly to the authenticated tenant context."""
        return bool(tenant_id and resource_tenant_id and tenant_id == resource_tenant_id)
