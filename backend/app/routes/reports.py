import hashlib

from flask import jsonify, request

from app.extensions import db
from app.routes import api_bp
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus
from app.services.dispatch import DispatchService


@api_bp.route("/report", methods=["POST"])
def create_report():
    data = request.get_json(silent=True) or {}
    source_id = data.get("source_id")
    cause_category = data.get("cause_category")

    if not source_id or not cause_category:
        return jsonify({"error": "source_id and cause_category are required"}), 400

    source = WaterSource.query.get(source_id)
    if not source:
        return jsonify({"error": "Water source not found"}), 404

    phone = data.get("reporter_phone")
    phone_hash = hashlib.sha256(phone.encode()).hexdigest() if phone else None

    report = Report(
        source_id=source.id,
        reporter_phone_hash=phone_hash,
        cause_category=cause_category.upper(),
        channel="web",
    )
    source.status = WaterSourceStatus.UNSAFE
    db.session.add(report)
    db.session.flush()

    repair_case = DispatchService().create_from_report(report)
    db.session.commit()

    return jsonify(
        {
            "message": "Report submitted. Repair team notified.",
            "report_id": report.id,
            "repair_case_id": repair_case.id,
            "eta": repair_case.eta.isoformat() if repair_case.eta else None,
        }
    ), 201
