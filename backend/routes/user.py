from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db, cache
from models import Trek, Booking, User
from utils.decorators import role_required

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.get("/dashboard")
@role_required("trekker")
def dashboard():
    user_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(status="Open").order_by(Trek.id.desc()).all()
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).limit(5).all()
    return jsonify({
        "available_treks": [t.to_dict() for t in treks],
        "my_bookings": [b.to_dict() for b in bookings],
    })


@user_bp.get("/treks")
@role_required("trekker")
def browse_treks():
    difficulty = request.args.get("difficulty", "All")
    location = request.args.get("location", "All")
    q = request.args.get("q", "").strip()

    cache_key = f"open_treks_{difficulty}_{location}_{q}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    query = Trek.query.filter_by(status="Open")
    if difficulty and difficulty != "All":
        query = query.filter(Trek.difficulty == difficulty)
    if location and location != "All":
        query = query.filter(Trek.location == location)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Trek.name.ilike(like), Trek.location.ilike(like)))

    treks = [t.to_dict() for t in query.order_by(Trek.id.desc()).all()]
    cache.set(cache_key, treks, timeout=60)
    return jsonify(treks)


@user_bp.post("/treks/<int:trek_id>/book")
@role_required("trekker")
def book_trek(trek_id):
    user_id = int(get_jwt_identity())
    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return jsonify({"error": "This trek is not open for booking"}), 400

    if trek.available_slots <= 0:
        return jsonify({"error": "No slots available"}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status="Booked").first()
    if existing:
        return jsonify({"error": "You have already booked this trek"}), 409

    trek.available_slots -= 1
    booking = Booking(user_id=user_id, trek_id=trek_id, status="Booked", payment_status="N/A")
    db.session.add(booking)
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass
    return jsonify(booking.to_dict()), 201


@user_bp.put("/bookings/<int:booking_id>/cancel")
@role_required("trekker")
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first_or_404()

    if booking.status != "Booked":
        return jsonify({"error": "Only active bookings can be cancelled"}), 400

    booking.status = "Cancelled"
    trek = Trek.query.get(booking.trek_id)
    if trek and trek.available_slots < trek.total_slots:
        trek.available_slots += 1
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass
    return jsonify(booking.to_dict())


@user_bp.get("/bookings")
@role_required("trekker")
def my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


@user_bp.get("/history")
@role_required("trekker")
def history():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).filter(
        Booking.status.in_(["Completed", "Cancelled"])
    ).order_by(Booking.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


@user_bp.get("/profile")
@role_required("trekker")
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@user_bp.put("/profile")
@role_required("trekker")
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}

    if "name" in data and data["name"]:
        user.name = data["name"]
    if "contact_number" in data:
        user.contact_number = data["contact_number"]
    if data.get("new_password"):
        if not data.get("current_password") or not user.check_password(data["current_password"]):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.set_password(data["new_password"])

    db.session.commit()
    return jsonify(user.to_dict())


@user_bp.post("/export-history")
@role_required("trekker")
def export_history():
    """Trigger an async Celery job to export the user's booking history as CSV."""
    from tasks import export_booking_history_csv
    user_id = int(get_jwt_identity())
    task = export_booking_history_csv.delay(user_id)
    return jsonify({"message": "Export started. You'll be notified when it's ready.", "task_id": task.id}), 202


@user_bp.get("/export-history/<task_id>")
@role_required("trekker")
def export_status(task_id):
    from extensions import celery_app
    result = celery_app.AsyncResult(task_id)
    payload = {"state": result.state}
    if result.state == "SUCCESS":
        payload["file"] = result.result
    elif result.state == "FAILURE":
        payload["error"] = str(result.info)
    return jsonify(payload)
