"""Drought prediction: rainfall + historical dry-well reports -> WARNING SMS."""

import requests
from flask import current_app

from app.extensions import db
from app.models.report import Report
from app.models.water_source import WaterSource
from app.services.sms_gateway import send_sms

DRY_WELL_CAUSES = {"DRY_WELL", "LOW_WATER", "DROUGHT"}


class PredictionEngine:
    def fetch_rainfall(self, district: str | None = None) -> float | None:
        url = current_app.config.get("WEATHER_API_URL")
        api_key = current_app.config.get("WEATHER_API_KEY")
        if not url or not api_key:
            return None
        try:
            response = requests.get(
                url,
                params={"district": district, "apikey": api_key},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            return float(data.get("rainfall_mm", 0))
        except (requests.RequestException, ValueError, TypeError):
            current_app.logger.warning("Weather API unavailable for district %s", district)
            return None

    def dry_report_count(self, district: str, days: int = 30) -> int:
        from datetime import datetime, timedelta, timezone

        since = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            Report.query.join(WaterSource)
            .filter(
                WaterSource.district == district,
                Report.cause_category.in_(DRY_WELL_CAUSES),
                Report.timestamp >= since,
            )
            .count()
        )

    def should_warn(self, district: str, rainfall_threshold_mm: float = 10.0) -> bool:
        rainfall = self.fetch_rainfall(district)
        dry_count = self.dry_report_count(district)
        low_rain = rainfall is not None and rainfall < rainfall_threshold_mm
        return low_rain or dry_count >= 3

    def broadcast_warning(self, district: str, phone_numbers: list[str]) -> int:
        message = (
            f"⚠ DROUGHT WARNING ({district}): Low rainfall reported. "
            "Conserve water. Text STATUS <ID> for your source."
        )
        sent = 0
        for phone in phone_numbers:
            if send_sms(phone, message):
                sent += 1
        return sent
