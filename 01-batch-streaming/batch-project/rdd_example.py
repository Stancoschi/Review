from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("rdd_example").getOrCreate()
sc = spark.sparkContext

lines = sc.textFile("data/sales.csv")
header = lines.first()
rows = lines.filter(lambda l: l != header).map(lambda l: l.split(","))
good = rows.filter(lambda r: r[3] != "" and float(r[3]) > 0)          # filter
pairs = good.map(lambda r: (r[2], float(r[3])))                       # map
totals = pairs.reduceByKey(lambda a, b: a + b)                        # aggregate

print("partitions:", good.getNumPartitions())
print(sorted(totals.collect()))
spark.stop()
