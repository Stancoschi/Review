import json
import random
import sys
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

# usage: python producer.py [number_of_orders] [delay_seconds]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
DELAY = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: str(k).encode("utf-8"),
)

for i in range(1, N + 1):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    customer = random.randint(101, 105)
    amount = round(random.uniform(5, 100), 2)
    if i % 10 == 0:
        amount = -1.0                      # every 10th order is bad on purpose
    producer.send("orders", key=customer,
                  value={"order_id": i, "customer_id": customer, "amount": amount, "ts": now})
    if i % 2 == 0:                          # half of the orders get a payment
        producer.send("payments", key=customer,
                      value={"order_id": i, "method": random.choice(["card", "cash"]), "pay_ts": now})
    time.sleep(DELAY)

producer.flush()
print("sent", N, "orders")
