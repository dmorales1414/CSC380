from flask import Blueprint, json, request, jsonify, current_app
from db_models import User
from database import db
from werkzeug.security import generate_password_hash
from utils.auth import get_authenticated_user
from utils.events import user_created_event, user_password_changed_event, user_profile_updated_event
from utils.hateoas_helper import game_links, offer_links, user_links

# Blueprint for user routes
bp_users = Blueprint("users", __name__, url_prefix="/users")

# Create a new user
@bp_users.post("")
def create_user():
    user_redis_client = current_app.redis_client

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

    # Clear cached users
    user_redis_client.delete("all_users")

    db.session.add(user)
    db.session.commit()

    # Notify the user of their account creation
    user_created_event(user)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "links": user_links(user)
    }), 201

# Get a specific user's details
@bp_users.get("/<int:user_id>")
def get_user(user_id):
    user_redis_client = current_app.redis_client
    cache_key = f"user_{user_id}"

    cached = user_redis_client.get(cache_key)

    if cached:
        print(f"CACHE HIT: user")
        return jsonify(json.loads(cached))

    print(f"CACHE MISS: user")
    
    user = User.query.get_or_404(user_id)

    user_results = [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "links": user_links(user)
    }]

    # Cache the user details for 1 minute (60 seconds)
    user_redis_client.setex(cache_key, 60, json.dumps(user_results))

    return jsonify(user_results)

# Get all users
@bp_users.get("")
def get_users():
    user_redis_client = current_app.redis_client
    cache_key = "all_users"

    cached = user_redis_client.get(cache_key)

    if cached:
        print(f"CACHE HIT: all_users")
        return jsonify(json.loads(cached))
    
    print(f"CACHE MISS: all_users")

    users = User.query.all()
    
    all_user_results = [{
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "links": user_links(user)
        }
        for user in users
    ]

    # Cache the user details for 1 minute (60 seconds)
    user_redis_client.setex(cache_key, 60, json.dumps(all_user_results))

    return jsonify(all_user_results)

# Update a specific user's details
@bp_users.put("/<int:user_id>")
def update_user(user_id):
    user_redis_client = current_app.redis_client

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Forbidden: Must be the authenticated user to update their own details"}, 403

    data = request.json
    user.name = data["name"]
    user.address = data["address"]
    db.session.commit()

    # Notify the user of their profile update
    user_profile_updated_event(user)

    # Clear cached user details
    user_redis_client.delete(f"user_{user_id}")
    user_redis_client.delete("all_users")

    return "", 204

@bp_users.patch("/<int:user_id>")
def update_password(user_id):
    user_redis_client = current_app.redis_client

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Forbidden: Must be the authenticated user to update their own password"}, 403

    data = request.json
    user.password = generate_password_hash(data["password"])
    db.session.commit()

    # Notify the user of their password change
    user_password_changed_event(user)

    # Clear cached user details
    user_redis_client.delete(f"user_{user_id}")
    
    return "", 204