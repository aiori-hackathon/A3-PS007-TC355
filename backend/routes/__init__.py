"""
Routes package for PrivacyGuard IPv6
"""
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.device_routes import device_bp
from backend.routes.monitoring_routes import monitoring_bp
from backend.routes.simulation_routes import simulation_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.privacy_routes import privacy_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.evaluation_routes import evaluation_bp

__all__ = [
    "dashboard_bp",
    "device_bp",
    "monitoring_bp",
    "simulation_bp",
    "alert_bp",
    "privacy_bp",
    "analytics_bp",
    "evaluation_bp"
]
