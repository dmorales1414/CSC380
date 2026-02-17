from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER", "kafka:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_notification(from_email, from_password, to_list, subject, body):
    if isinstance(to_list, str):
        to_list = [to_list]

    event = {
        "from_email": from_email,
        "from_password": from_password,
        "to": to_list,
        "subject": subject,
        "body": body
    }

    producer.send("notifications", event)
    producer.flush()
