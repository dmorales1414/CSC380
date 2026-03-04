import json
import logging
import smtplib
from email.message import EmailMessage
from kafka import KafkaConsumer
from ssl import create_default_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("email_consumer")

SMTP_SERVER = "smtp.ethereal.email"
SMTP_PORT = 587

logger.info("Email service started. Waiting for events...")

consumer = KafkaConsumer(
    "user.created",
    "offer.created",
    "offer.accepted",
    "offer.rejected",
    "user.updated",
    "user.password_changed",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="email-service",
)

ssl_ctx = create_default_context()

logger.info("Email service has now started. Waiting for events...")

for message in consumer:
    event = message.value
    topic = message.topic

    try:
        msg = EmailMessage()
        msg["From"] = event["from_email"]
        msg["To"] = ", ".join(event["to"])

        # USER EVENTS MESSAGES
        if topic == "user.created":
            msg["Subject"] = "Welcome to Retro Game Trading Platform"
            msg.set_content(
                f"Hello {event['user_name']}, your account has been created successfully."
            )

        elif topic == "user.password_changed":
            msg["Subject"] = "Password Changed"
            msg.set_content(
                f"Hello {event['user_name']}, your password was updated."
            )

        elif topic == "user.profile_updated":
            msg["Subject"] = "Profile Updated"
            msg.set_content(
                f"Hello {event['user_name']}, your profile was updated."
            )

        # OFFER CREATED MESSAGES
        elif topic == "offer.created":
            if event["type"] == "recipient":
                msg["Subject"] = "New Offer Received"
                msg.set_content(
                    f"You have received a new offer (ID: {event['offer_id']})."
                )
            else:
                msg["Subject"] = "Offer Sent Successfully"
                msg.set_content(
                    f"Your offer (ID: {event['offer_id']}) was sent successfully."
                )

        # OFFER STATUS MESSAGES
        elif topic in ["offer.accepted", "offer.rejected"]:
            status = topic.split(".")[1]
            msg["Subject"] = f"Offer {status.title()}"
            msg.set_content(
                f"Offer ID {event['offer_id']} was {status}."
            )

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=ssl_ctx)
            server.login(event["from_email"], event["from_password"])
            server.send_message(msg)

        logger.info("EMAIL SENT via topic %s", topic)

    except Exception as e:
        logger.error("FAILED TO SEND EMAIL: %s", e)