from flask import jsonify

from app.routes import api_bp
from app.models.water_source import WaterSource


@api_bp.route("/sources", methods=["GET"])
def get_sources():
    sources = WaterSource.query.all()
    return jsonify(
        {
            "type": "FeatureCollection",
            "features": [s.to_geojson_feature() for s in sources],
        }
    )
