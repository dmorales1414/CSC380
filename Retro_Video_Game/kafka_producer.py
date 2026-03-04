from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER", "kafka:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_event(topic: str, payload: dict):
    producer.send(topic, payload)
    producer.flush()


