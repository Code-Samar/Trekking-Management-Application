from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """Only Trekkers (Users) can self-register. Admin and Staff are created
    programmatically / by Admin respectively."""
    data = request.get_json(force=True) or {}
    required = ["name", "email", "password", "confirm_password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Passwords do not match"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=data["email"].lower().strip()).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        contact_number=data.get("contact_number"),
        role="trekker",
        status="active",
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful. Please log in.", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""
    role = data.get("role")  # optional hint from the login screen (admin/staff/trekker)

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.status == "blacklisted":
        return jsonify({"error": "Your account has been blacklisted. Contact Admin."}), 403

    if role and role != user.role:
        return jsonify({"error": f"This account is not registered as {role}"}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name, "email": user.email},
    )
    return jsonify({"access_token": token, "user": user.to_dict()}), 200
