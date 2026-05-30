import hashlib
import re

from flask import current_app

from app.extensions import db
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus
from app.services.dispatch import DispatchService
from app.services.sms_gateway import send_sms

STATUS_PATTERN = re.compile(r"^STATUS\s+(\w+)$", re.IGNORECASE)
CAUSE_PATTERN = re.compile(r"^CAUSE\s+(\w+)\s+(\w+)$", re.IGNORECASE)
TIPS_PATTERN = re.compile(r"^TIPS$", re.IGNORECASE)

STATUS_EMOJI = {
    WaterSourceStatus.SAFE: "🟢",
    WaterSourceStatus.CAUTION: "🟡",
    WaterSourceStatus.UNSAFE: "🔴",
}

STATUS_LABEL = {
    WaterSourceStatus.SAFE: "Safe",
    WaterSourceStatus.CAUTION: "Caution - boil water",
    WaterSourceStatus.UNSAFE: "Unsafe",
}


class SMSHandler:
    """Parse inbound SMS commands and route to database / dispatch."""

    def __init__(self):
        self.dispatch = DispatchService()

    def handle(self, from_number: str, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "⚠ Send STATUS <ID> or CAUSE <ID> <CODE>."

        if match := STATUS_PATTERN.match(text):
            return self._handle_status(match.group(1))

        if match := CAUSE_PATTERN.match(text):
            return self._handle_cause(from_number, match.group(1), match.group(2))

        if TIPS_PATTERN.match(text):
            return self._handle_tips()

        return "⚠ Unknown command. Try: STATUS WELL123 or CAUSE WELL123 BROKEN_PUMP"

    def _handle_status(self, source_id: str) -> str:
        source = db.session.get(WaterSource, source_id.upper())
        if not source:
            return f"⚠ Unknown water point: {source_id}"

        emoji = STATUS_EMOJI.get(source.status, "⚪")
        label = STATUS_LABEL.get(source.status, source.status)
        tested = source.last_tested.strftime("%Y-%m-%d") if source.last_tested else "N/A"
        return f"{emoji} {source.name}: {label}. Last tested: {tested}."

    def _handle_cause(self, phone: str, source_id: str, cause: str) -> str:
        source_id = source_id.upper()
        source = db.session.get(WaterSource, source_id)
        if not source:
            return f"⚠ Unknown water point: {source_id}"

        phone_hash = hashlib.sha256(phone.encode()).hexdigest() if phone else None
        report = Report(
            source_id=source.id,
            reporter_phone_hash=phone_hash,
            cause_category=cause.upper(),
            channel="sms",
        )
        source.status = WaterSourceStatus.UNSAFE
        db.session.add(report)
        db.session.flush()

        repair_case = self.dispatch.create_from_report(report)
        db.session.commit()

        eta_hours = current_app.config.get("REPAIR_DEFAULT_ETA_HOURS", 48)
        return (
            f"✅ Reported. Repair team notified. "
            f"ETA: {eta_hours} hours. Ref: #{repair_case.id}"
        )

    def _handle_tips(self) -> str:
        return (
            "📖 Tips: Boil water if yellow. Avoid red sources. "
            "Text STATUS <ID> for updates. Stay safe!"
        )
