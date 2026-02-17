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
    "notifications",
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

    try:
        msg = EmailMessage()
        msg["From"] = event["from_email"]
        msg["To"] = ", ".join(event["to"])
        msg["Subject"] = event["subject"]
        msg.set_content(event["body"])

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=ssl_ctx)
            server.login(event["from_email"], event["from_password"])
            server.send_message(msg)

        logger.info("EMAIL SENT → %s", event["to"])

    except Exception as e:
        logger.error("FAILED TO SEND EMAIL: %s", e)
