from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    """Unified user model for Admin, Trek Staff, and Trekkers (User)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default="trekker")  # admin | staff | trekker
    status = db.Column(db.String(20), nullable=False, default="active")  # active | blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Staff-only extra fields
    experience_years = db.Column(db.Integer)
    specialization = db.Column(db.String(120))

    bookings = db.relationship("Booking", backref="user", lazy=True, foreign_keys="Booking.user_id")
    assigned_treks = db.relationship("Trek", backref="assigned_staff", lazy=True, foreign_keys="Trek.assigned_staff_id")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "contact_number": self.contact_number,
            "role": self.role,
            "status": self.status,
            "experience_years": self.experience_years,
            "specialization": self.specialization,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy | Moderate | Hard
    duration_days = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), nullable=False, default="Pending")
    # Pending | Approved | Open | Closed | Completed
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="trek", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": self.assigned_staff.name if self.assigned_staff else None,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description,
        }


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Booked")  # Booked | Cancelled | Completed
    payment_status = db.Column(db.String(20), default="N/A")
    # Note: duplicate-booking prevention (no 2 active "Booked" rows for same
    # user+trek) is enforced in application logic, not a DB constraint,
    # so a cancelled booking doesn't block re-booking the same trek.

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name if self.trek else None,
            "location": self.trek.location if self.trek else None,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "status": self.status,
            "payment_status": self.payment_status,
            "start_date": self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            "end_date": self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
        }
