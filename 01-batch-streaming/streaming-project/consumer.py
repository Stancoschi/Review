import json
import sys
from kafka import KafkaConsumer

# usage: python consumer.py [topic] [group_id]
topic = sys.argv[1] if len(sys.argv) > 1 else "orders"
group = sys.argv[2] if len(sys.argv) > 2 else "demo-group"

consumer = KafkaConsumer(
    topic,
    bootstrap_servers="localhost:9092",
    group_id=group,
    auto_offset_reset="earliest",
    value_deserializer=lambda b: json.loads(b.decode("utf-8")),
)

for msg in consumer:
    print(f"partition={msg.partition} offset={msg.offset} value={msg.value}")
