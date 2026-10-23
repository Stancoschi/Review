import logging
import sqlite3
from pyspark.sql import SparkSession, functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sink")

DB = "orders_sink.db"
SCHEMA = "order_id int, customer_id int, amount double, ts string"


def setup():
    con = sqlite3.connect(DB)
    con.execute("create table if not exists orders(order_id int primary key, customer_id int, amount real, ts text)")
    con.execute("create table if not exists done_batches(batch_id int primary key)")
    con.commit()
    con.close()


def write_batch(df, batch_id):
    # Spark can replay a batch after a crash, so I remember which batches are finished.
    con = sqlite3.connect(DB)
    try:
        if con.execute("select 1 from done_batches where batch_id = ?", (batch_id,)).fetchone():
            log.info("batch %s already written, skipping", batch_id)
            return
        rows = [(r.order_id, r.customer_id, r.amount, r.ts) for r in df.collect()]
        con.executemany("insert or replace into orders values (?,?,?,?)", rows)
        con.execute("insert into done_batches values (?)", (batch_id,))
        con.commit()                       # data and batch id are saved together
        log.info("batch %s written, %s rows", batch_id, len(rows))
    except Exception:
        con.rollback()
        log.exception("batch %s failed", batch_id)
        raise                              # Spark will retry the batch
    finally:
        con.close()


if __name__ == "__main__":
    setup()
    spark = SparkSession.builder.appName("sqlite_sink").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    raw = (spark.readStream.format("kafka")
           .option("kafka.bootstrap.servers", "localhost:9092")
           .option("subscribe", "orders").option("startingOffsets", "earliest").load())
    orders = raw.select(F.from_json(F.col("value").cast("string"), SCHEMA).alias("d")).select("d.*") \
                .filter("order_id is not null and amount > 0")
    (orders.writeStream.foreachBatch(write_batch)
           .option("checkpointLocation", "checkpoints/sqlite_sink")
           .start().awaitTermination())
