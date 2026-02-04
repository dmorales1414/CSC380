from flask import Blueprint, request, jsonify
from db_models import User
from database import db
from werkzeug.security import generate_password_hash
from auth import get_authenticated_user

# Blueprint for user routes
bp_users = Blueprint("users", __name__, url_prefix="/users")

# Create a new user
@bp_users.post("")
def create_user():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return {"error": "Email exists"}, 409

    data["password"] = generate_password_hash(data["password"])
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id, name=user.name, email=user.email, address=user.address), 201

# Get a specific user's details
@bp_users.get("/<int:user_id>")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(id=user.id, name=user.name, email=user.email, address=user.address)

# Get all users
@bp_users.get("")
def get_users():
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address
        }
        for user in users
    ])

# Update a specific user's details
@bp_users.put("/<int:user_id>")
def update_user(user_id):
    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Forbidden: Must be the authenticated user to update their own details"}, 403

    data = request.json
    user.name = data["name"]
    user.address = data["address"]
    db.session.commit()
    return "", 204
