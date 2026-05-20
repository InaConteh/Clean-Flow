from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api_bp
from app.models.repair_case import RepairCase, RepairStatus
from app.services.dispatch import DispatchService


@api_bp.route("/repairs", methods=["GET"])
@jwt_required()
def list_repairs():
    status = request.args.get("status")
    query = RepairCase.query
    if status:
        query = query.filter_by(status=status)
    cases = query.order_by(RepairCase.created_at.desc()).limit(100).all()
    return jsonify(
        {
            "repairs": [
                {
                    "id": c.id,
                    "report_id": c.report_id,
                    "assigned_team": c.assigned_team,
                    "eta": c.eta.isoformat() if c.eta else None,
                    "status": c.status,
                }
                for c in cases
            ]
        }
    )


@api_bp.route("/repairs/<int:case_id>", methods=["PATCH"])
@jwt_required()
def update_repair(case_id: int):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in {
        RepairStatus.REPORTED,
        RepairStatus.ASSIGNED,
        RepairStatus.IN_PROGRESS,
        RepairStatus.RESOLVED,
    }:
        return jsonify({"error": "Invalid status"}), 400
    case = DispatchService().advance(case_id, new_status)
    if not case:
        return jsonify({"error": "Repair case not found"}), 404
    return jsonify({"id": case.id, "status": case.status})
