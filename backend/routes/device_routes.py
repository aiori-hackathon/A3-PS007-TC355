"""
Device Routes
Manages simulated IoT devices, connection status, and privacy address rotations.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path
from backend.services.network_simulator import NetworkSimulator

device_bp = Blueprint("devices", __name__, url_prefix="/api/devices")
simulator = NetworkSimulator()

@device_bp.route("", methods=["GET"])
def get_devices():
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT device_id, tenant_id, device_name, device_type, current_ipv6, current_pseudonym, status, last_event_at, created_at
        FROM devices
        WHERE tenant_id = ?
        ORDER BY device_id ASC
        """, (tenant_id,))
        devices = [dict(r) for r in cur.fetchall()]
        return jsonify({"success": True, "tenant_id": tenant_id, "devices": devices})
    finally:
        conn.close()

@device_bp.route("/<device_id>/events", methods=["GET"])
def get_device_events(device_id):
    tenant_id = request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("SELECT current_pseudonym FROM devices WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
        dev = cur.fetchone()
        if not dev:
            return jsonify({"success": False, "error": "Device not found"}), 404

        pseudo = dev["current_pseudonym"]
        cur.execute("""
        SELECT event_id, timestamp, tenant_id, event_type, pseudonym, source_ipv6, payload_json, is_suspicious, status
        FROM network_events
        WHERE tenant_id = ? AND pseudonym = ?
        ORDER BY timestamp DESC
        LIMIT 20
        """, (tenant_id, pseudo))
        events = [dict(r) for r in cur.fetchall()]
        return jsonify({"success": True, "device_id": device_id, "pseudonym": pseudo, "events": events})
    finally:
        conn.close()

@device_bp.route("/<device_id>/rotate-address", methods=["POST"])
def rotate_address(device_id):
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        result = simulator.rotate_device_address(conn, device_id, tenant_id)
        if not result.get("success"):
            return jsonify(result), 404
        return jsonify(result)
    finally:
        conn.close()

@device_bp.route("/<device_id>/connect", methods=["POST"])
def connect_device(device_id):
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("UPDATE devices SET status = 'CONNECTED' WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Device not found"}), 404
        return jsonify({"success": True, "device_id": device_id, "status": "CONNECTED"})
    finally:
        conn.close()

@device_bp.route("/<device_id>/disconnect", methods=["POST"])
def disconnect_device(device_id):
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    conn = get_db_connection(get_db_path(current_app))
    try:
        cur = conn.cursor()
        cur.execute("UPDATE devices SET status = 'DISCONNECTED' WHERE device_id = ? AND tenant_id = ?", (device_id, tenant_id))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Device not found"}), 404
        return jsonify({"success": True, "device_id": device_id, "status": "DISCONNECTED"})
    finally:
        conn.close()
