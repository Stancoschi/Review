import sqlite3
import sys
import logging
from pyspark.sql import SparkSession, functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("batch")

# Job parameters
SALES = "data/sales.csv"
ORDERS = "data/orders.json"
DB = "data/customers.db"
OUT = "out"
PARTITIONS = 4


def read_sales(spark, path=SALES):
    return spark.read.csv(path, header=True, inferSchema=True)


def read_orders(spark, path=ORDERS):
    # nested JSON: one row per item in the order
    df = spark.read.option("multiLine", True).json(path)
    return df.select("order_id", F.col("customer.name").alias("customer"),
                     F.explode("items").alias("item")) \
             .select("order_id", "customer", "item.sku", "item.qty")


def read_customers(spark, path=DB):
    # relational source, read with the standard sqlite3 driver
    con = sqlite3.connect(path)
    rows = con.execute("select customer_id, name, city from customers").fetchall()
    con.close()
    return spark.createDataFrame(rows, "customer_id int, name string, city string")


def split_valid(df):
    # a bad row goes to quarantine with a reason, it does not stop the job
    reason = (F.when(F.col("amount").isNull(), "amount missing")
               .when(F.col("amount") <= 0, "amount not positive")
               .when(F.col("customer_id").isNull(), "customer missing"))
    df = df.withColumn("reject_reason", reason)
    return df.filter("reject_reason is null").drop("reject_reason"), \
           df.filter("reject_reason is not null")


def run(spark, out=OUT):
    sales = read_sales(spark)
    customers = read_customers(spark)
    orders = read_orders(spark)

    valid, rejected = split_valid(sales)
    n_in, n_valid, n_rej = sales.count(), valid.count(), rejected.count()
    log.info("rows read=%s valid=%s rejected=%s", n_in, n_valid, n_rej)
    if n_in != n_valid + n_rej:
        raise ValueError("rows lost during validation")

    rejected.write.mode("overwrite").option("header", True).csv(f"{out}/quarantine")

    result = (valid.join(customers, "customer_id")
                   .groupBy("city", "category")
                   .agg(F.sum("amount").alias("total"), F.count("*").alias("orders")))
    result.repartition(PARTITIONS).write.mode("overwrite").parquet(f"{out}/sales_by_city")
    orders.write.mode("overwrite").parquet(f"{out}/order_items")

    log.info("output rows=%s", spark.read.parquet(f"{out}/sales_by_city").count())
    return n_in, n_valid, n_rej


if __name__ == "__main__":
    spark = SparkSession.builder.appName("sales_batch").getOrCreate()
    try:
        run(spark)
    except Exception:
        log.exception("job failed")
        sys.exit(1)
    finally:
        spark.stop()
