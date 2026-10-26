"""
Evaluation Routes
Runs the reproducible benchmark evaluation suite and returns TP, FP, TN, FN,
Recall, Precision, False-Positive Rate, F1-Score, and privacy metrics.
"""
from flask import Blueprint, jsonify, request, current_app
from backend.database import get_db_connection, get_db_path
from backend.services.evaluation_service import EvaluationService

evaluation_bp = Blueprint("evaluation", __name__, url_prefix="/api/evaluation")

@evaluation_bp.route("/run", methods=["POST"])
def run_evaluation():
    data = request.get_json(silent=True) or {}
    tenant_id = data.get("tenant_id") or request.args.get("tenant_id", "tenant-alpha")
    
    conn = get_db_connection(get_db_path(current_app))
    try:
        results = EvaluationService.run_evaluation_suite(conn, tenant_id=tenant_id)
        return jsonify({"success": True, "results": results})
    finally:
        conn.close()

@evaluation_bp.route("/results", methods=["GET"])
def get_results():
    conn = get_db_connection(get_db_path(current_app))
    try:
        latest = EvaluationService.get_latest_results(conn)
        if not latest:
            return jsonify({
                "success": True,
                "has_run": False,
                "message": "No evaluation has been executed yet. Click 'Run Evaluation' to benchmark the system."
            })
        return jsonify({
            "success": True,
            "has_run": True,
            "results": latest
        })
    finally:
        conn.close()
