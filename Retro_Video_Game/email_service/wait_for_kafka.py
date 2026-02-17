import time
from kafka import KafkaProducer

while True:
    try:
        KafkaProducer(bootstrap_servers="kafka:9092")
        print("Kafka is ready")
        break
    except:
        print("Waiting for Kafka...")
        time.sleep(3)
