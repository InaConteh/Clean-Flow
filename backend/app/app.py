import os
from flask import Flask
from app.extensions import db

# Import the models package to register WaterSource, Report, etc. with SQLAlchemy
import app.models

def create_app():
    """Application factory to configure and initialize the Flask app."""
    app = Flask(__name__)

    # Supabase Connection string - Use environment variables for security
    # Fallback string provided for local testing (replace with your credentials)
    DEFAULT_CONN = "postgresql://postgres:[inaconteh2006]@db.nanpgezjrnbgeokdswmr.supabase.co:5432/postgres"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', DEFAULT_CONN)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with this app instance
    db.init_app(app)

    # Register custom CLI commands
    @app.cli.command("init-db")
    def init_db():
        """Creates all database tables in Supabase."""
        print("Connecting to Supabase and initializing tables...")
        try:
            with app.app_context():
                db.create_all()
            print("Success: All 5 water utility tables successfully created!")
        except Exception as e:
            print(f"Error creating tables: {e}")

    # Simple health-check route to verify database connection
    @app.route('/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {"status": "healthy", "database": "connected"}, 200
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}, 500

    return app

# Main entry point for running the development server
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)