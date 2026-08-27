"""
Optional helper to populate the app with demo data for testing/demoing.
Run once after the backend has started (so the DB + admin already exist):

    python seed_demo_data.py
"""
from datetime import date, timedelta
from app import create_app
from extensions import db
from models import User, Trek, Booking

app = create_app()

with app.app_context():
    if User.query.filter_by(role="staff").count() == 0:
        staff1 = User(name="Vikas Singh", email="vikas@tma.com", role="staff", status="active",
                      contact_number="9876543210", experience_years=5, specialization="High Altitude")
        staff1.set_password("Staff@123")
        staff2 = User(name="Neha Joshi", email="neha@tma.com", role="staff", status="active",
                      contact_number="9123456780", experience_years=3, specialization="First Aid")
        staff2.set_password("Staff@123")
        db.session.add_all([staff1, staff2])
        db.session.commit()
        print("Seeded staff: vikas@tma.com / Staff@123, neha@tma.com / Staff@123")

    if User.query.filter_by(role="trekker").count() == 0:
        u1 = User(name="Amit Sharma", email="amit@tma.com", role="trekker", status="active", contact_number="9876543210")
        u1.set_password("User@123")
        u2 = User(name="Priya Patel", email="priya@tma.com", role="trekker", status="active", contact_number="9123456780")
        u2.set_password("User@123")
        db.session.add_all([u1, u2])
        db.session.commit()
        print("Seeded trekkers: amit@tma.com / User@123, priya@tma.com / User@123")

    if Trek.query.count() == 0:
        staff = User.query.filter_by(role="staff").first()
        treks = [
            Trek(name="Everest Base Camp", location="Nepal", difficulty="Hard", duration_days=12,
                 total_slots=20, available_slots=8, status="Open", assigned_staff_id=staff.id,
                 start_date=date.today() + timedelta(days=20), end_date=date.today() + timedelta(days=32),
                 description="A classic high-altitude trek to Everest Base Camp."),
            Trek(name="Roopkund Trek", location="Uttarakhand", difficulty="Moderate", duration_days=7,
                 total_slots=15, available_slots=7, status="Open", assigned_staff_id=staff.id,
                 start_date=date.today() + timedelta(days=10), end_date=date.today() + timedelta(days=17),
                 description="Mystery lake trek in the Himalayas."),
            Trek(name="Hampta Pass", location="Himachal", difficulty="Moderate", duration_days=5,
                 total_slots=12, available_slots=0, status="Closed", assigned_staff_id=staff.id,
                 start_date=date.today() + timedelta(days=5), end_date=date.today() + timedelta(days=10),
                 description="Cross-over trek from Kullu to Lahaul valley."),
            Trek(name="Kedarkantha Trek", location="Uttarakhand", difficulty="Easy", duration_days=6,
                 total_slots=18, available_slots=18, status="Open", assigned_staff_id=staff.id,
                 start_date=date.today() + timedelta(days=30), end_date=date.today() + timedelta(days=36),
                 description="Great winter trek for beginners."),
        ]
        db.session.add_all(treks)
        db.session.commit()
        print("Seeded 4 demo treks.")

    print("Demo data seeding complete.")
