from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class UserRole:
    DISTRICT_OFFICIAL = "district_official"
    TECHNICAL_TEAM = "technical_team"
    WATER_COMMITTEE_HEAD = "water_committee_head"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    preferred_language = db.Column(db.String(10), default="en")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
