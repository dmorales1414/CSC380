from flask import Blueprint, request, jsonify
from db_models import User
from database import db
from werkzeug.security import generate_password_hash
from utils.auth import get_authenticated_user
from kafka_producer import send_notification
from utils.hateoas_helper import game_links, offer_links, user_links

# Blueprint for user routes
bp_users = Blueprint("users", __name__, url_prefix="/users")

# Create a new user
@bp_users.post("")
def create_user():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return {"error": "Email exists"}, 409
    
    user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        address=data["address"],
        smtp_email=data.get("smtp_email"),
        smtp_password=data.get("smtp_password")
    )

    db.session.add(user)
    db.session.commit()

    send_notification(
        from_email=user.smtp_email,
        from_password=user.smtp_password,
        to_list=[user.email],
        subject="Welcome to Retro Game Trading Platform",
        body=f"Hello {user.name}, and welcome to our Retro Game Trading Platform! Your account has been successfully created."
    )
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "_links": user_links(user)
    }), 201

# Get a specific user's details
@bp_users.get("/<int:user_id>")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "_links": user_links(user)
    })

# Get all users
@bp_users.get("")
def get_users():
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "_links": user_links(user)
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
    send_notification(
        from_email=user.smtp_email,
        from_password=user.smtp_password,
        to_list=[user.email],
        subject="Profile Updated",
        body=f"Hello {user.name}, your profile details have been updated successfully."
    )
    return "", 204

@bp_users.patch("/<int:user_id>")
def update_password(user_id):
    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Forbidden: Must be the authenticated user to update their own password"}, 403

    data = request.json
    user.password = generate_password_hash(data["password"])
    db.session.commit()
    send_notification(
        from_email=user.smtp_email,
        from_password=user.smtp_password,
        to_list=[user.email],
        subject="Password Changed",
        body=f"Hello {user.name}, your password has been changed successfully."
    )
    return "", 204