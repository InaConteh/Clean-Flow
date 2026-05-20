from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models.repair_case import RepairCase, RepairStatus
from app.models.report import Report


class DispatchService:
    """Repair dispatch workflow: Reported -> Assigned -> In Progress -> Resolved."""

    def create_from_report(self, report: Report) -> RepairCase:
        eta_hours = current_app.config.get("REPAIR_DEFAULT_ETA_HOURS", 48)
        case = RepairCase(
            report_id=report.id,
            assigned_team=self._team_for_source(report.source_id),
            eta=datetime.now(timezone.utc) + timedelta(hours=eta_hours),
            status=RepairStatus.ASSIGNED,
        )
        db.session.add(case)
        return case

    def advance(self, case_id: int, new_status: str) -> RepairCase | None:
        case = RepairCase.query.get(case_id)
        if not case:
            return None
        case.status = new_status
        if new_status == RepairStatus.RESOLVED:
            case.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
        return case

    def _team_for_source(self, source_id: str) -> str:
        return f"team-{source_id[:3].lower()}"
