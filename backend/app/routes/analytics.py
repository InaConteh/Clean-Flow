import csv
import json
import io
from flask import Blueprint, jsonify, request, make_response
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import role_required
from app.models.user import UserRole

analytics_bp = Blueprint("analytics", __name__)
service = AnalyticsService()

@analytics_bp.route("/admin/analytics/metrics", methods=["GET"])
@role_required([UserRole.DISTRICT_OFFICIAL])
def get_metrics():
    downtime = service.get_reduction_in_downtime()
    trends = service.get_regional_failure_trends()
    return jsonify({
        "reduction_in_downtime_hours": downtime,
        "regional_failure_trends": trends
    })

@analytics_bp.route("/admin/analytics/export", methods=["GET"])
@role_required([UserRole.DISTRICT_OFFICIAL])
def export_analytics():
    format = request.args.get("format", "json").lower()
    downtime = service.get_reduction_in_downtime()
    trends = service.get_regional_failure_trends()

    data = {
        "metric": "Reduction in Downtime (hours)",
        "value": downtime,
        "trends": trends
    }

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Reduction in Downtime (hours)", downtime])
        writer.writerow([])
        writer.writerow(["District", "Failure Count"])
        for trend in trends:
            writer.writerow([trend["district"], trend["count"]])

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=analytics_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    else: # Default JSON
        return jsonify(data)
