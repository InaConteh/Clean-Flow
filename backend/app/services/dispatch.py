from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models.repair_case import RepairCase, RepairStatus
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus
from app.services.sms_gateway import send_sms


class DispatchService:
    """Repair dispatch workflow: Reported -> Assigned -> In Progress -> Resolved."""

    def create_from_report(self, report: Report) -> RepairCase:
        eta_hours = current_app.config.get("REPAIR_DEFAULT_ETA_HOURS", 48)
        case = RepairCase(
            report_id=report.id,
            assigned_team=self._team_for_source(report.source_id),
            eta=datetime.now(timezone.utc) + timedelta(hours=eta_hours),
            status=RepairStatus.REPORTED,
        )
        db.session.add(case)
        return case

    def advance(self, case_id: int, new_status: str) -> RepairCase | None:
        case = db.session.get(RepairCase, case_id)
        if not case:
            return None

        old_status = case.status
        case.status = new_status

        if new_status == RepairStatus.ASSIGNED and old_status == RepairStatus.REPORTED:
            # Notify technical team
            team_contact = f"contact-{case.assigned_team}" # Placeholder
            message = f"New repair assigned: Case #{case.id} for Source {case.report.source_id}. Status: Reported."
            send_sms(team_contact, message)

        elif new_status == RepairStatus.IN_PROGRESS:
            # Send return SMS with ETA
            reporter_phone = "UNKNOWN" # Logic to retrieve reporter phone if needed
            # In a real scenario, we might have the reporter phone from the report
            # but it is hashed in the current model. For this implementation,
            # we focus on the requirement of triggering a return SMS.
            message = f"Update on Case #{case.id}: Work is now in progress. ETA for completion: {case.eta}."
            # Since reporter_phone_hash is used, actual phone might not be available
            # unless stored elsewhere. Assuming some mechanism to get it or using committee_phone.
            source = db.session.get(WaterSource, case.report.source_id)
            if source and hasattr(source, 'committee_phone') and source.committee_phone:
                send_sms(source.committee_phone, message)

        elif new_status == RepairStatus.RESOLVED:
            case.resolved_at = datetime.now(timezone.utc)
            # Update source status back to Green
            source = db.session.get(WaterSource, case.report.source_id)
            if source:
                source.status = WaterSourceStatus.SAFE

        db.session.commit()
        return case

    def _team_for_source(self, source_id: str) -> str:
        return f"team-{source_id[:3].lower()}"
