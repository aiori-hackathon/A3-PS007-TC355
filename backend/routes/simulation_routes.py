"""
Simulation Routes
Triggers simulated normal traffic, Rogue Router Advertisements, NDP rate anomalies,
and environment resets for hackathon demonstrations.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path, reset_database
from backend.services.network_simulator import NetworkSimulator

simulation_bp = Blueprint("simulation", __name__, url_prefix="/api/simulation")
simulator = NetworkSimulator()

@simulation_bp.route("/normal-traffic", methods=["POST"])
def simulate_normal_traffic():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    count = int(data.get("count", 5))
    
    conn = get_db_connection(get_db_path(current_app))
    try:
        events = simulator.generate_normal_traffic(conn, tenant_id, count=count)
        return jsonify({
            "success": True,
            "message": f"Generated {len(events)} normal IPv6 packets (NDP + Authorised RA)",
            "events_generated": len(events),
            "tenant_id": tenant_id
        })
    finally:
        conn.close()

@simulation_bp.route("/rogue-ra", methods=["POST"])
def simulate_rogue_ra():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    source = data.get("source_ipv6", "fe80::dead:beef:666")
    prefix = data.get("advertised_prefix", "2001:db8:evil::/64")

    conn = get_db_connection(get_db_path(current_app))
    try:
        result = simulator.simulate_rogue_ra(conn, tenant_id, unauthorized_source=source, bogus_prefix=prefix)
        return jsonify({
            "success": True,
            "message": "Simulated Rogue Router Advertisement injected",
            "alert_generated": result.get("alert_created", False),
            "alert_id": result.get("alert_id"),
            "detection": result.get("alert_info"),
            "event_id": result.get("event_id")
        })
    finally:
        conn.close()

@simulation_bp.route("/ndp-anomaly", methods=["POST"])
def simulate_ndp_anomaly():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    burst_count = int(data.get("burst_count", 55))
    target_pseudonym = data.get("pseudonym")

    conn = get_db_connection(get_db_path(current_app))
    try:
        result = simulator.simulate_ndp_anomaly(conn, tenant_id, burst_count=burst_count, target_pseudonym=target_pseudonym)
        return jsonify({
            "success": True,
            "message": f"Simulated {burst_count} high-rate NDP Neighbor Solicitations",
            "alert_generated": result.get("alert_created", False) if result else True,
            "alert_id": result.get("alert_id") if result else None,
            "detection": result.get("alert_info") if result else None
        })
    finally:
        conn.close()

@simulation_bp.route("/reset", methods=["POST"])
def reset_demo():
    reset_database(get_db_path(current_app))
    return jsonify({
        "success": True,
        "message": "Demonstration environment reset successfully. Initial 5 devices re-seeded per tenant."
    })
