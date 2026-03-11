from flask import Blueprint, request, jsonify, current_app
from db_models import Game, User, Offer
from database import db
from utils.events import offer_created_event, offer_status_event
from utils.auth import get_authenticated_user
from utils.hateoas_helper import offer_links
import json

# Blueprint for offer routes
bp_offers = Blueprint("offers", __name__, url_prefix="/offers")

# Create a new offer
@bp_offers.post("/users/<int:user_id>")
def create_offer(user_id):
    offer_redis_client = current_app.redis_client

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    data = request.json

    offer = Offer(
        offered_game_id=data["offered_game_id"],
        requested_game_id=data["requested_game_id"],
        from_user_id=user_id,
        to_user_id=data["to_user_id"]
    )

    db.session.add(offer)
    db.session.commit()

    # Clear cached offers for both the sender and the recipient
    offer_redis_client.delete(f"user_offers_{user_id}")
    offer_redis_client.delete(f"user_offers_{data['to_user_id']}")

    sender = User.query.get_or_404(offer.from_user_id)
    receiver = User.query.get_or_404(offer.to_user_id)

    # Notify both the sender and the recipient of the new offer
    offer_created_event(offer, sender, receiver)

    return jsonify({
        "id": offer.id,
        "status": offer.status,
        "links": offer_links(offer)
    }), 201

# Get all current offers of a specific user
@bp_offers.get("/users/<int:user_id>")
def my_offers(user_id):
    # Caches the offers for 1 minute (60 seconds)
    offer_redis_client = current_app.redis_client
    cache_key = f"user_offers_{user_id}"

    cached = offer_redis_client.get(cache_key)

    # If the offers are cached, return the cached version instead of querying the database
    if cached:
        print(f"CACHE HIT: offers")
        return jsonify(json.loads(cached))

    print(f"CACHE MISS: offers")

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    offers = Offer.query.filter(
        (Offer.from_user_id == user.id) |
        (Offer.to_user_id == user.id)
    )

    offer_results = [{
        "id": o.id,
        "status": o.status,
        "from": o.from_user_id,
        "to": o.to_user_id,
        "links": offer_links(o)
    } for o in offers]

    offer_redis_client.setex(cache_key, 60, json.dumps(offer_results))

    return jsonify(offer_results)


# Update the status of a specific offer
# Example: { "status": "accepted" }
@bp_offers.put("/users/<int:user_id>/<int:offer_id>")
def update_offer(user_id, offer_id):
    offer_redis_client = current_app.redis_client

    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    offer = Offer.query.get_or_404(offer_id)

    if user.id != offer.to_user_id:
        return {"error": "Forbidden: Must be the recipient of the offer to update it"}, 403

    # Will force status to be either accepted or rejected
    status = request.json.get("status")
    if status not in ["accepted", "rejected"]:
        return {"error": "Invalid status choose either 'accepted' or 'rejected'"}, 400

    offer.status = status
    db.session.commit()

    # Update cached offers for the user and recupient
    offer_redis_client.delete(f"user_offers_{user_id}")
    offer_redis_client.delete(f"user_offers_{offer.to_user_id}")

    sender = User.query.get_or_404(offer.from_user_id)
    recipient = User.query.get_or_404(offer.to_user_id)

    # Notifies both the sender and the recipient that the offer status has been updated
    offer_status_event(offer, sender, recipient)

    return jsonify({
        "id": offer.id,
        "status": offer.status,
        "from": offer.from_user_id,
        "to": offer.to_user_id,
        "links": offer_links(offer)
    }), 204
