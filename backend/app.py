"""
PrivacyGuard IPv6 - Flask Application Factory
Initializes database, CORS, route blueprints, and error handlers.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timezone
import os

from backend.config import Config
from backend.database import init_db, get_db_connection, get_db_path
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.device_routes import device_bp
from backend.routes.monitoring_routes import monitoring_bp
from backend.routes.simulation_routes import simulation_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.privacy_routes import privacy_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.evaluation_routes import evaluation_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure database schema is initialised
    with app.app_context():
        init_db(get_db_path(app))

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(privacy_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(evaluation_bp)

    # Settings API endpoints
    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        conn = get_db_connection(get_db_path(app))
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value, updated_at FROM app_settings")
            rows = cur.fetchall()
            settings = {r["key"]: r["value"] for r in rows}
            return jsonify({
                "success": True,
                "settings": {
                    "ndp_threshold": int(settings.get("ndp_threshold", 50)),
                    "ndp_window_seconds": int(settings.get("ndp_window_seconds", 10)),
                    "pseudonym_lifetime_seconds": int(settings.get("pseudonym_lifetime_seconds", 300)),
                    "session_lifetime_seconds": int(settings.get("session_lifetime_seconds", 180)),
                    "event_retention_days": int(settings.get("event_retention_days", 7)),
                    "simulation_speed": settings.get("simulation_speed", "1x")
                }
            })
        finally:
            conn.close()

    @app.route("/api/settings", methods=["PUT"])
    def update_settings():
        data = request.get_json(silent=True) or {}
        conn = get_db_connection(get_db_path(app))
        try:
            cur = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            
            allowed_keys = [
                "ndp_threshold",
                "ndp_window_seconds",
                "pseudonym_lifetime_seconds",
                "session_lifetime_seconds",
                "event_retention_days",
                "simulation_speed"
            ]

            # Validation
            if "ndp_threshold" in data:
                val = int(data["ndp_threshold"])
                if val < 1 or val > 1000:
                    return jsonify({"success": False, "error": "ndp_threshold must be between 1 and 1000"}), 400
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('ndp_threshold', ?, ?)", (str(val), now_iso))

            if "ndp_window_seconds" in data:
                val = int(data["ndp_window_seconds"])
                if val < 1 or val > 3600:
                    return jsonify({"success": False, "error": "ndp_window_seconds must be between 1 and 3600"}), 400
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('ndp_window_seconds', ?, ?)", (str(val), now_iso))

            if "pseudonym_lifetime_seconds" in data:
                val = int(data["pseudonym_lifetime_seconds"])
                if val < 5 or val > 86400:
                    return jsonify({"success": False, "error": "pseudonym_lifetime_seconds must be between 5 and 86400"}), 400
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('pseudonym_lifetime_seconds', ?, ?)", (str(val), now_iso))

            if "session_lifetime_seconds" in data:
                val = int(data["session_lifetime_seconds"])
                if val < 5 or val > 86400:
                    return jsonify({"success": False, "error": "session_lifetime_seconds must be between 5 and 86400"}), 400
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('session_lifetime_seconds', ?, ?)", (str(val), now_iso))

            if "event_retention_days" in data:
                val = int(data["event_retention_days"])
                if val < 1 or val > 365:
                    return jsonify({"success": False, "error": "event_retention_days must be between 1 and 365"}), 400
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('event_retention_days', ?, ?)", (str(val), now_iso))

            if "simulation_speed" in data:
                cur.execute("INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES ('simulation_speed', ?, ?)", (str(data["simulation_speed"]), now_iso))

            conn.commit()
            return jsonify({"success": True, "message": "Settings updated successfully"})
        finally:
            conn.close()

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
