from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db, cache
from models import Trek, Booking, User
from utils.decorators import role_required

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")


@staff_bp.get("/dashboard")
@role_required("staff")
def dashboard():
    staff_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    total_participants = 0
    ongoing = 0
    for t in treks:
        total_participants += Booking.query.filter_by(trek_id=t.id).filter(Booking.status != "Cancelled").count()
        if t.status == "Open":
            ongoing += 1
    return jsonify({
        "assigned_treks": len(treks),
        "total_participants": total_participants,
        "ongoing_treks": ongoing,
        "treks": [t.to_dict() for t in treks],
    })


def _own_trek_or_404(trek_id, staff_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_id:
        return None
    return trek


@staff_bp.get("/treks")
@role_required("staff")
def my_treks():
    staff_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).order_by(Trek.id.desc()).all()
    return jsonify([t.to_dict() for t in treks])


@staff_bp.put("/treks/<int:trek_id>")
@role_required("staff")
def update_trek(trek_id):
    staff_id = int(get_jwt_identity())
    trek = _own_trek_or_404(trek_id, staff_id)
    if trek is None:
        return jsonify({"error": "You are not assigned to this trek"}), 403

    data = request.get_json(force=True) or {}
    if "available_slots" in data:
        new_avail = int(data["available_slots"])
        if new_avail < 0 or new_avail > trek.total_slots:
            return jsonify({"error": f"available_slots must be between 0 and {trek.total_slots}"}), 400
        trek.available_slots = new_avail
    if "status" in data:
        if data["status"] not in ("Pending", "Approved", "Open", "Closed", "Completed"):
            return jsonify({"error": "Invalid status"}), 400
        trek.status = data["status"]

    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass
    return jsonify(trek.to_dict())


@staff_bp.put("/treks/<int:trek_id>/complete")
@role_required("staff")
def mark_completed(trek_id):
    staff_id = int(get_jwt_identity())
    trek = _own_trek_or_404(trek_id, staff_id)
    if trek is None:
        return jsonify({"error": "You are not assigned to this trek"}), 403

    trek.status = "Completed"
    db.session.commit()

    # Mark all active bookings for this trek as Completed too
    bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status == "Booked").all()
    for b in bookings:
        b.status = "Completed"
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass
    return jsonify(trek.to_dict())


@staff_bp.get("/treks/<int:trek_id>/participants")
@role_required("staff")
def participants(trek_id):
    staff_id = int(get_jwt_identity())
    trek = _own_trek_or_404(trek_id, staff_id)
    if trek is None:
        return jsonify({"error": "You are not assigned to this trek"}), 403

    bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status != "Cancelled").all()
    return jsonify([b.to_dict() for b in bookings])
