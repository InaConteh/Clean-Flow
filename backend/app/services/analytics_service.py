from sqlalchemy import func
from app.models.repair_case import RepairCase, RepairStatus
from app.models.report import Report
from app.models.water_source import WaterSource
from app.extensions import db

class AnalyticsService:
    def get_reduction_in_downtime(self):
        """
        Metric: The average time a source remains 'Red' before being resolved.
        Calculated as the difference between Report.timestamp and RepairCase.resolved_at.
        """
        resolved_cases = db.session.query(RepairCase, Report).\
            join(Report, RepairCase.report_id == Report.id).\
            filter(RepairCase.status == RepairStatus.RESOLVED).\
            filter(RepairCase.resolved_at.isnot(None)).all()

        if not resolved_cases:
            return 0.0

        total_downtime = 0
        for case, report in resolved_cases:
            downtime = (case.resolved_at - report.timestamp).total_seconds()
            total_downtime += downtime

        avg_downtime_hours = (total_downtime / len(resolved_cases)) / 3600
        return round(avg_downtime_hours, 2)

    def get_regional_failure_trends(self):
        """
        Identify regional failure trends by counting reports per district.
        """
        trends = db.session.query(WaterSource.district, func.count(Report.id)).\
            join(Report, WaterSource.id == Report.source_id).\
            group_by(WaterSource.district).all()

        return [{"district": row[0], "count": row[1]} for row in trends]
