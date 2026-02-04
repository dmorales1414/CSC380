from flask import Blueprint, request, jsonify
from db_models import Game, User, Offer
from database import db
from auth import get_authenticated_user


# Blueprint for offer routes
bp_offers = Blueprint("offers", __name__, url_prefix="/offers")

# Create a new offer
@bp_offers.post("/users/<int:user_id>")
def create_offer(user_id):
    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    data = request.json
    offer = Offer(
        offered_game_id=data["offered_game_id"],
        requested_game_id=data["requested_game_id"],
        from_user_id=user.id,
        to_user_id=data["to_user_id"]
    )

    db.session.add(offer)
    db.session.commit()
    return jsonify(id=offer.id, status=offer.status), 201

# Get all current offers of a specific user
@bp_offers.get("/users/<int:user_id>")
def my_offers(user_id):
    user = get_authenticated_user()
    if not user or user.id != user_id:
        return {"error": "Unauthorized Access"}, 401

    offers = Offer.query.filter(
        (Offer.from_user_id == user.id) |
        (Offer.to_user_id == user.id)
    )

    return jsonify([{
        "id": o.id,
        "status": o.status,
        "from": o.from_user_id,
        "to": o.to_user_id
    } for o in offers])

# Update the status of a specific offer
# Example: { "status": "accepted" }
@bp_offers.put("/users/<int:user_id>/<int:offer_id>")
def update_offer(user_id, offer_id):
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
    return jsonify(id=offer.id, status=offer.status), 204
