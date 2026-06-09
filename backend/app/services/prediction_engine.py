"""Drought prediction: rainfall + historical dry-well reports -> WARNING SMS."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests
from flask import current_app

from app.extensions import db
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus
from app.services.sms_gateway import send_sms

DRY_WELL_CAUSES = {"DRY_WELL", "LOW_WATER", "DROUGHT", "SEASONAL", "DRY"}


class PredictionEngine:
    RAINFALL_THRESHOLD_MM = 10.0
    DRY_REPORT_WINDOW_DAYS = 7
    DRY_REPORT_HISTORY_DAYS = 14
    DRY_REPORT_INCREASE_FACTOR = 1.5
    MIN_RISING_REPORTS = 2

    def get_sources_by_district(self, district: str) -> list[WaterSource]:
        return WaterSource.query.filter(WaterSource.district == district).all()

    def get_district_coordinates(self, district: str) -> tuple[float, float] | None:
        sources = self.get_sources_by_district(district)
        if not sources:
            return None
        lat = sum(source.latitude for source in sources) / len(sources)
        lon = sum(source.longitude for source in sources) / len(sources)
        return lat, lon

    def fetch_rainfall(self, district: str) -> float | None:
        url = current_app.config.get("WEATHER_API_URL")
        api_key = current_app.config.get("WEATHER_API_KEY")
        coords = self.get_district_coordinates(district)
        if not url or not coords:
            return None

        latitude, longitude = coords
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "UTC",
        }
        if "open-meteo" in url:
            params.update({"daily": "rain_sum", "current_weather": True})
        elif api_key:
            params["apikey"] = api_key

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "open-meteo" in url:
                daily = data.get("daily", {})
                rain_sum = daily.get("rain_sum") or []
                if isinstance(rain_sum, list) and rain_sum:
                    return float(rain_sum[-1])
                current_weather = data.get("current_weather", {})
                return float(current_weather.get("precipitation", 0.0))

            return float(data.get("rainfall_mm", 0.0))
        except (requests.RequestException, ValueError, TypeError) as exc:
            current_app.logger.warning(
                "Weather API unavailable for district %s: %s",
                district,
                exc,
            )
            return None

    def report_count(self, district: str, days: int) -> int:
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

    def rising_dry_trend(self, district: str) -> bool:
        recent = self.report_count(district, self.DRY_REPORT_WINDOW_DAYS)
        prior = self.report_count(district, self.DRY_REPORT_HISTORY_DAYS) - recent
        if recent < self.MIN_RISING_REPORTS:
            return False
        if prior == 0:
            return recent >= self.MIN_RISING_REPORTS
        return recent >= prior * self.DRY_REPORT_INCREASE_FACTOR

    def should_warn(self, district: str) -> bool:
        rainfall = self.fetch_rainfall(district)
        if rainfall is None:
            return False

        low_rain = rainfall < self.RAINFALL_THRESHOLD_MM
        rising_reports = self.rising_dry_trend(district)
        current_app.logger.info(
            "Drought check %s: rainfall=%s, low_rain=%s, rising_reports=%s",
            district,
            rainfall,
            low_rain,
            rising_reports,
        )
        return low_rain and rising_reports

    def collect_phone_numbers(self, district: str) -> list[str]:
        phones = {
            source.committee_phone.strip()
            for source in self.get_sources_by_district(district)
            if source.committee_phone
        }
        return [phone for phone in phones if phone]

    def update_sources_for_warning(self, district: str) -> int:
        sources = self.get_sources_by_district(district)
        updated = 0
        now = datetime.now(timezone.utc)
        for source in sources:
            if source.status != WaterSourceStatus.CAUTION:
                source.status = WaterSourceStatus.CAUTION
                updated += 1
            source.last_tested = now
        db.session.commit()
        return updated

    def build_warning_message(self, district: str) -> str:
        return (
            f"⚠ Drought warning for {district}. Low rain + rising dry well reports. "
            "Conserve water and check your source."
        )

    def broadcast_warning(self, district: str, phone_numbers: list[str]) -> int:
        if not phone_numbers:
            current_app.logger.info("No SMS targets for %s", district)
            return 0

        message = self.build_warning_message(district)
        sent = 0
        for phone in phone_numbers:
            if send_sms(phone, message):
                sent += 1
        return sent

    def check_and_warn(self, district: str) -> int:
        if not district or not self.should_warn(district):
            return 0

        warned = self.broadcast_warning(district, self.collect_phone_numbers(district))
        self.update_sources_for_warning(district)
        return warned
