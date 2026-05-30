"""Initialize database tables for Supabase/PostgreSQL."""

import os
from app import create_app
from app.extensions import db
# Import models to ensure they are registered with SQLAlchemy
from app.models import WaterSource, Report, MaintenanceLog, RepairCase, User

def setup_database():
    """
    Creates all tables in the database specified by SQLALCHEMY_DATABASE_URI.
    For Supabase, the user should set the DATABASE_URL environment variable
    to their Supabase connection string.
    """
    app = create_app()

    with app.app_context():
        print("Creating all tables in the database...")
        try:
            db.create_all()
            print("Successfully created all tables.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            print("\nMake sure DATABASE_URL is set correctly in your environment.")

if __name__ == "__main__":
    setup_database()
