import sys
from pyspark.sql import SparkSession, functions as F

BROKER = "localhost:9092"

ORDER_SCHEMA = "order_id int, customer_id int, amount double, ts string"
PAYMENT_SCHEMA = "order_id int, method string, pay_ts string"


def read_topic(spark, topic, schema):
    raw = (spark.readStream.format("kafka")
           .option("kafka.bootstrap.servers", BROKER)
           .option("subscribe", topic)
           .option("startingOffsets", "earliest")
           .load())
    parsed = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("d")).select("d.*")
    return parsed


def stateless(spark):
    # projection + filter: each record is handled on its own
    orders = read_topic(spark, "orders", ORDER_SCHEMA)
    good = orders.filter("amount > 0").select("order_id", "customer_id", "amount")
    return good.writeStream.format("console").outputMode("append") \
               .option("checkpointLocation", "checkpoints/stateless").start()


def windowed(spark):
    # aggregation over 1 minute windows, keeps state between records
    orders = read_topic(spark, "orders", ORDER_SCHEMA) \
        .filter("amount > 0") \
        .withColumn("ts", F.to_timestamp("ts")) \
        .withWatermark("ts", "2 minutes")
    agg = (orders.groupBy(F.window("ts", "1 minute"), "customer_id")
                 .agg(F.sum("amount").alias("total"), F.count("*").alias("orders")))
    return agg.writeStream.format("console").outputMode("update") \
              .option("truncate", False) \
              .option("checkpointLocation", "checkpoints/windowed").start()


def joined(spark):
    # stream-stream join: an order with its payment (within 5 minutes)
    orders = read_topic(spark, "orders", ORDER_SCHEMA) \
        .withColumn("ts", F.to_timestamp("ts")).withWatermark("ts", "2 minutes")
    payments = read_topic(spark, "payments", PAYMENT_SCHEMA) \
        .withColumn("pay_ts", F.to_timestamp("pay_ts")).withWatermark("pay_ts", "2 minutes")
    both = orders.join(
        payments,
        F.expr("orders.order_id = payments.order_id AND pay_ts >= ts AND pay_ts <= ts + interval 5 minutes")
        if False else
        (orders["order_id"] == payments["order_id"]) &
        (payments["pay_ts"] >= orders["ts"]) &
        (payments["pay_ts"] <= orders["ts"] + F.expr("interval 5 minutes")))
    out = both.select(orders["order_id"], "customer_id", "amount", "method")
    return out.writeStream.format("console").outputMode("append") \
              .option("checkpointLocation", "checkpoints/joined").start()


MODES = {"stateless": stateless, "windowed": windowed, "joined": joined}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stateless"
    spark = SparkSession.builder.appName(f"stream_{mode}").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    query = MODES[mode](spark)
    query.awaitTermination()
