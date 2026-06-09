import random
from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.water_source import WaterSource, WaterSourceStatus
from app.models.report import Report
from app.models.repair_case import RepairCase, RepairStatus
from app.models.maintenance_log import MaintenanceLog

DISTRICTS = [
    "Freetown", "Bo", "Kenema", "Makeni", "Koidu", 
    "Port Loko", "Waterloo", "Lunsar", "Kabala", "Moyamba"
]

CAUSE_OPTIONS = ["DROUGHT", "BROKEN_PUMP", "DRY_WELL", "CONTAMINATION", "OVERUSE", "SEASONAL"]
MAINTENANCE_TASKS = ["PUMP_LUBRICATION", "FILTER_CLEANING", "CHLORINATION", "WELL_DESILTING", "STRUCTURAL_PATCH"]

def seed_database():
    print("Clearing existing data...")
    db.session.query(RepairCase).delete()
    db.session.query(Report).delete()
    db.session.query(MaintenanceLog).delete()
    db.session.query(WaterSource).delete()
    db.session.query(User).delete()
    db.session.commit()

    print("Seeding users...")
    # 1. District Official
    official = User(username="official", role=UserRole.DISTRICT_OFFICIAL, preferred_language="en")
    official.set_password("password")
    db.session.add(official)

    # 2. Technical Team
    tech = User(username="tech", role=UserRole.TECHNICAL_TEAM, preferred_language="en")
    tech.set_password("password")
    db.session.add(tech)

    # 3. Water Committee Head
    committee = User(username="committee", role=UserRole.WATER_COMMITTEE_HEAD, preferred_language="kri")
    committee.set_password("password")
    db.session.add(committee)

    print("Seeding water sources...")
    now = datetime.now(timezone.utc)
    
    # Pre-populate 50 water sources
    sources = []
    for i in range(1, 51):
        district = random.choice(DISTRICTS)
        status_roll = random.random()
        
        if status_roll < 0.70:
            status = WaterSourceStatus.SAFE
        elif status_roll < 0.90:
            status = WaterSourceStatus.CAUTION
        else:
            status = WaterSourceStatus.UNSAFE

        lat = round(random.uniform(7.5, 9.8), 4)
        lon = round(random.uniform(-13.2, -10.5), 4)
        
        days_tested = random.randint(1, 30)
        last_tested_date = now - timedelta(days=days_tested)
        
        phone_suffix = "".join(random.choices("0123456789", k=6))
        phone = f"+23276{phone_suffix}"
        
        source = WaterSource(
            id=f"WELL{i:03d}",
            name=f"{district} Pump {i}",
            latitude=lat,
            longitude=lon,
            status=status,
            last_tested=last_tested_date,
            district=district,
            committee_phone=phone,
            preferred_language=random.choice(["en", "kri"]),
            created_at=now - timedelta(days=random.randint(100, 365))
        )
        db.session.add(source)
        sources.append(source)
    
    db.session.flush()  # Generate IDs and make sure sources are in session

    print("Seeding active reports, repairs, and maintenance logs...")
    for source in sources:
        if source.status == WaterSourceStatus.CAUTION:
            # Seed maintenance log
            log = MaintenanceLog(
                source_id=source.id,
                task_type=random.choice(MAINTENANCE_TASKS),
                scheduled_date=now + timedelta(days=random.randint(1, 14)),
                completion_status="pending",
                notes="Scheduled routine preventative maintenance check.",
                created_at=now - timedelta(days=random.randint(1, 5))
            )
            db.session.add(log)
            
        elif source.status == WaterSourceStatus.UNSAFE:
            # Seed active issue report and corresponding Repair Case
            cause = random.choice(CAUSE_OPTIONS)
            report_time = now - timedelta(hours=random.randint(2, 48))
            
            # Simple hash for reporter phone
            phone_hash = f"hashed_phone_{random.randint(1000, 9999)}"
            
            report = Report(
                source_id=source.id,
                reporter_phone_hash=phone_hash,
                cause_category=cause,
                timestamp=report_time,
                channel=random.choice(["sms", "web"])
            )
            db.session.add(report)
            db.session.flush()

            # Create Repair Case
            status_roll = random.random()
            if status_roll < 0.33:
                repair_status = RepairStatus.REPORTED
                assigned_team = None
                eta = None
            elif status_roll < 0.66:
                repair_status = RepairStatus.ASSIGNED
                assigned_team = f"team-{source.id[:3].lower()}"
                eta = report_time + timedelta(hours=48)
            else:
                repair_status = RepairStatus.IN_PROGRESS
                assigned_team = f"team-{source.id[:3].lower()}"
                eta = report_time + timedelta(hours=24)

            repair_case = RepairCase(
                report_id=report.id,
                assigned_team=assigned_team,
                eta=eta,
                status=repair_status,
                created_at=report_time
            )
            db.session.add(repair_case)

    print("Seeding historical resolved cases (for analytics)...")
    # Generate 15 resolved repair cases in the past to populate regional trends and downtime metrics
    for i in range(1, 16):
        source = random.choice(sources)
        # We want to represent a historical problem that is now resolved, so the source status remains SAFE
        cause = random.choice(CAUSE_OPTIONS)
        
        # Incident happened in the past (e.g. 5-30 days ago)
        days_ago = random.randint(5, 30)
        report_time = now - timedelta(days=days_ago)
        
        report = Report(
            source_id=source.id,
            reporter_phone_hash=f"hashed_phone_hist_{i}",
            cause_category=cause,
            timestamp=report_time,
            channel=random.choice(["sms", "web"])
        )
        db.session.add(report)
        db.session.flush()

        # Downtime lasted between 4 hours and 72 hours
        downtime_hours = random.randint(4, 72)
        resolved_time = report_time + timedelta(hours=downtime_hours)

        repair_case = RepairCase(
            report_id=report.id,
            assigned_team=f"team-{source.id[:3].lower()}",
            eta=report_time + timedelta(hours=48),
            status=RepairStatus.RESOLVED,
            created_at=report_time,
            resolved_at=resolved_time
        )
        db.session.add(repair_case)

        # Let's add completed maintenance logs too
        log = MaintenanceLog(
            source_id=source.id,
            task_type=random.choice(MAINTENANCE_TASKS),
            scheduled_date=report_time - timedelta(days=1),
            completion_status="completed",
            notes="Completed maintenance check. Everything is verified functional.",
            created_at=report_time - timedelta(days=5)
        )
        db.session.add(log)

    db.session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
