# Note:
# [AI Citation] AI generated this entrypoint script to ensure that the email consumer does not start until Kafka is ready. 
#       The script waits for Kafka to be available before starting the email consumer.

#!/bin/sh

echo "Waiting for Kafka..."
python wait_for_kafka.py

echo "Kafka is ready. Starting email consumer..."
python consumer.py
