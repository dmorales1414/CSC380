from flask import Blueprint, request, jsonify
from db_models import Game, User, Offer
from database import db
from kafka_producer import send_notification
from utils.auth import get_authenticated_user
from utils.hateoas_helper import offer_links

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
        from_user_id=user_id,
        to_user_id=data["to_user_id"]
    )

    db.session.add(offer)
    db.session.commit()

    sender = User.query.get_or_404(offer.from_user_id)
    receiver = User.query.get_or_404(offer.to_user_id)

    # Notify the recipient of the new offer
    send_notification(
        from_email=receiver.smtp_email,
        from_password=receiver.smtp_password,
        to_list=[sender.smtp_email],
        subject="New Offer Received",
        body=f"Offer ID: {offer.id}\nFrom user: {sender.name}\nTo user: {receiver.name}\nOffered Game ID: {offer.offered_game_id}\nRequested Game ID: {offer.requested_game_id}\nStatus: {offer.status}"
    )

    # Notify the sender that their offer has been created
    send_notification(
        from_email=sender.smtp_email,
        from_password=sender.smtp_password,
        to_list=[receiver.smtp_email],
        subject="Offer Created",
        body=f"Your offer (ID: {offer.id}) has been sent to {receiver.name}.\nOffered Game ID: {offer.offered_game_id}\nRequested Game ID: {offer.requested_game_id}\nStatus: {offer.status}"
    )

    return jsonify({
        "id": offer.id,
        "status": offer.status,
        "_links": offer_links(offer)
    }), 201

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
        "to": o.to_user_id,
        "_links": offer_links(o)
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

    sender = User.query.get_or_404(offer.from_user_id)
    recipient = User.query.get_or_404(offer.to_user_id)

    # Notifies the sender that their offer has been accepted or rejected
    send_notification(
        from_email=sender.smtp_email,
        from_password=sender.smtp_password,
        to_list=[recipient.smtp_email],
        subject=f"Offer {status.title()} (Sender Notification)",
        body=f"Offer (ID: {offer.id}) has been {status}\nFrom: {sender.name}\nTo: {recipient.name}"
    )

    # Notifies the recipient that they have {accepted/rejected} the offer
    send_notification(
        from_email=recipient.smtp_email,
        from_password=recipient.smtp_password,
        to_list=[sender.smtp_email],
        subject=f"Offer {status.title()} (Recipient Notification)",
        body=f"Offer (ID: {offer.id}) has been {status}\nFrom: {recipient.name}\nTo: {sender.name}"
    )

    return jsonify({
        "id": offer.id,
        "status": offer.status,
        "from": offer.from_user_id,
        "to": offer.to_user_id,
        "_links": offer_links(offer)
    }), 204
