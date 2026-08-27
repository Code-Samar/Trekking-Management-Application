from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db, cache
from models import User, Trek, Booking
from utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


# ---------- Dashboard ----------

@admin_bp.get("/dashboard")
@role_required("admin")
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="trekker").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_bookings = Booking.query.count()
    recent = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    return jsonify({
        "total_treks": total_treks,
        "total_users": total_users,
        "total_staff": total_staff,
        "total_bookings": total_bookings,
        "recent_bookings": [b.to_dict() for b in recent],
    })


# ---------- Treks ----------

@admin_bp.get("/treks")
@role_required("admin")
def list_treks():
    q = request.args.get("q", "").strip()
    cache_key = f"admin_treks_{q}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    query = Trek.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Trek.name.ilike(like), Trek.location.ilike(like)))
    treks = [t.to_dict() for t in query.order_by(Trek.id.desc()).all()]
    cache.set(cache_key, treks, timeout=60)
    return jsonify(treks)


@admin_bp.post("/treks")
@role_required("admin")
def create_trek():
    data = request.get_json(force=True) or {}
    required = ["name", "location", "difficulty", "duration_days", "total_slots"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    trek = Trek(
        name=data["name"].strip(),
        location=data["location"].strip(),
        difficulty=data["difficulty"],
        duration_days=int(data["duration_days"]),
        total_slots=int(data["total_slots"]),
        available_slots=int(data["total_slots"]),
        assigned_staff_id=data.get("assigned_staff_id"),
        status=data.get("status", "Pending"),
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        description=data.get("description"),
    )
    db.session.add(trek)
    db.session.commit()
    _invalidate_trek_cache()
    return jsonify(trek.to_dict()), 201


@admin_bp.put("/treks/<int:trek_id>")
@role_required("admin")
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json(force=True) or {}

    if "name" in data:
        trek.name = data["name"]
    if "location" in data:
        trek.location = data["location"]
    if "difficulty" in data:
        trek.difficulty = data["difficulty"]
    if "duration_days" in data:
        trek.duration_days = int(data["duration_days"])
    if "total_slots" in data:
        new_total = int(data["total_slots"])
        booked = trek.total_slots - trek.available_slots
        trek.total_slots = new_total
        trek.available_slots = max(0, new_total - booked)
    if "assigned_staff_id" in data:
        trek.assigned_staff_id = data["assigned_staff_id"]
    if "status" in data:
        trek.status = data["status"]
    if "start_date" in data:
        trek.start_date = _parse_date(data["start_date"])
    if "end_date" in data:
        trek.end_date = _parse_date(data["end_date"])
    if "description" in data:
        trek.description = data["description"]

    db.session.commit()
    _invalidate_trek_cache()
    return jsonify(trek.to_dict())


@admin_bp.delete("/treks/<int:trek_id>")
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if Booking.query.filter_by(trek_id=trek.id).count() > 0:
        return jsonify({"error": "Cannot delete a trek that has bookings. Close it instead."}), 400
    db.session.delete(trek)
    db.session.commit()
    _invalidate_trek_cache()
    return jsonify({"message": "Trek deleted"})


def _invalidate_trek_cache():
    # Clear all cached trek listing variants (admin + public "open treks" cache).
    # We can't wildcard-delete easily with simple flask-caching, so we clear
    # the whole cache namespace used for trek listings.
    try:
        cache.clear()
    except Exception:
        pass


# ---------- Staff ----------

@admin_bp.get("/staff")
@role_required("admin")
def list_staff():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="staff")
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(User.name.ilike(like), User.email.ilike(like)))
    return jsonify([s.to_dict() for s in query.order_by(User.id.desc()).all()])


@admin_bp.post("/staff")
@role_required("admin")
def create_staff():
    data = request.get_json(force=True) or {}
    required = ["name", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"].lower().strip()).first():
        return jsonify({"error": "Email already in use"}), 409

    staff = User(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        contact_number=data.get("contact_number"),
        role="staff",
        status="active",
        experience_years=data.get("experience_years"),
        specialization=data.get("specialization"),
    )
    staff.set_password(data["password"])
    db.session.add(staff)
    db.session.commit()
    return jsonify(staff.to_dict()), 201


@admin_bp.put("/staff/<int:staff_id>/status")
@role_required("admin")
def toggle_staff_status(staff_id):
    staff = User.query.filter_by(id=staff_id, role="staff").first_or_404()
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("active", "blacklisted"):
        return jsonify({"error": "status must be 'active' or 'blacklisted'"}), 400
    staff.status = new_status
    db.session.commit()
    return jsonify(staff.to_dict())


# ---------- Users (Trekkers) ----------

@admin_bp.get("/users")
@role_required("admin")
def list_users():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="trekker")
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(User.name.ilike(like), User.email.ilike(like)))
    return jsonify([u.to_dict() for u in query.order_by(User.id.desc()).all()])


@admin_bp.put("/users/<int:user_id>/status")
@role_required("admin")
def toggle_user_status(user_id):
    user = User.query.filter_by(id=user_id, role="trekker").first_or_404()
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("active", "blacklisted"):
        return jsonify({"error": "status must be 'active' or 'blacklisted'"}), 400
    user.status = new_status
    db.session.commit()
    return jsonify(user.to_dict())


# ---------- Bookings ----------

@admin_bp.get("/bookings")
@role_required("admin")
def list_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


# ---------- Reports ----------

@admin_bp.get("/reports/summary")
@role_required("admin")
def reports_summary():
    treks = Trek.query.all()
    data = []
    for t in treks:
        booked_count = Booking.query.filter_by(trek_id=t.id).filter(Booking.status != "Cancelled").count()
        data.append({
            "trek_id": t.id,
            "trek_name": t.name,
            "location": t.location,
            "status": t.status,
            "total_slots": t.total_slots,
            "available_slots": t.available_slots,
            "bookings": booked_count,
        })
    return jsonify(sorted(data, key=lambda x: x["bookings"], reverse=True))
