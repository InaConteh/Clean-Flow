from flask import jsonify, request

from app.routes import api_bp
from app.models.water_source import WaterSource, WaterSourceStatus
from app.models.user import UserRole
from app.services.auth_service import role_required
from app.extensions import db


@api_bp.route("/sources", methods=["GET"])
def get_sources():
    sources = WaterSource.query.all()
    return jsonify(
        {
            "type": "FeatureCollection",
            "features": [s.to_geojson_feature() for s in sources],
        }
    )


@api_bp.route("/admin/sources/<source_id>", methods=["PATCH"])
@role_required([UserRole.DISTRICT_OFFICIAL, UserRole.WATER_COMMITTEE_HEAD])
def update_source(source_id: str):
    """Local source management for Committee Heads and Officials."""
    source = db.session.get(WaterSource, source_id)
    if not source:
        return jsonify({"error": "Water source not found"}), 404

    data = request.get_json(silent=True) or {}

    if "status" in data:
        new_status = data["status"]
        if new_status in [WaterSourceStatus.SAFE, WaterSourceStatus.CAUTION, WaterSourceStatus.UNSAFE]:
            source.status = new_status

    if "name" in data:
        source.name = data["name"]

    db.session.commit()
    return jsonify(source.to_geojson_feature()["properties"])
