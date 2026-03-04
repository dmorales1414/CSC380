from kafka_producer import send_event

# OFFER EVENTS
def offer_created_event(offer, sender, recipient):
    # Event for recipient
    send_event("offer.created", {
        "type": "recipient",
        "offer_id": offer.id,
        "from_user": sender.name,
        "to_user": recipient.name,
        "from_email": recipient.smtp_email,
        "from_password": recipient.smtp_password,
        "to": [recipient.email]
    })

    # Event for sender
    send_event("offer.created", {
        "type": "sender",
        "offer_id": offer.id,
        "from_user": sender.name,
        "to_user": recipient.name,
        "from_email": sender.smtp_email,
        "from_password": sender.smtp_password,
        "to": [sender.email]
    })

def offer_status_event(offer, sender, recipient):
    topic = f"offer.{offer.status}"  # offer.accepted or offer.rejected

    # Event for sender
    send_event(topic, {
        "type": "sender",
        "offer_id": offer.id,
        "status": offer.status,
        "from_email": sender.smtp_email,
        "from_password": sender.smtp_password,
        "to": [sender.email]
    })

    # Event for recipient
    send_event(topic, {
        "type": "recipient",
        "offer_id": offer.id,
        "status": offer.status,
        "from_email": recipient.smtp_email,
        "from_password": recipient.smtp_password,
        "to": [recipient.email]
    })

# USER EVENTS

def user_created_event(user):
    send_event("user.created", {
        "user_name": user.name,
        "from_email": user.smtp_email,
        "from_password": user.smtp_password,
        "to": [user.email]
    })


def user_password_changed_event(user):
    send_event("user.password_changed", {
        "user_name": user.name,
        "from_email": user.smtp_email,
        "from_password": user.smtp_password,
        "to": [user.email]
    })


def user_profile_updated_event(user):
    send_event("user.profile_updated", {
        "user_name": user.name,
        "from_email": user.smtp_email,
        "from_password": user.smtp_password,
        "to": [user.email]
    })