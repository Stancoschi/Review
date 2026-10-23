# Sales batch job (PySpark)

This is a small batch job I built to practice Spark. I read sales data from a few places, remove the bad rows, and write a summary.

## What I did

1. I read `sales.csv` (orders), `orders.json` (orders with items nested inside) and `customers.db` (a SQLite table).
2. I check every sales row. If the amount is missing or not positive, or the customer is missing, I send the row to `out/quarantine` together with the reason. The job keeps going.
3. I join the good rows with the customers and add up sales by city and category.
4. I write the result as Parquet in `out/sales_by_city`, and the flattened order items in `out/order_items`.

With my sample data: 8 rows in, 5 good, 3 rejected.

## Files

- `batch_job.py` - the job itself
- `rdd_example.py` - the same kind of work with RDDs (filter, map, reduceByKey)
- `test_batch_job.py` - three small tests I wrote
- `data/` - the sample input

## Settings

I kept them at the top of `batch_job.py`: the input file paths, the output folder (`out`) and the number of output partitions (4).

## How I run it

I need Java 17 or 21 and Python.

    pip install -r requirements.txt
    python -m pytest -v
    spark-submit batch_job.py
    spark-submit rdd_example.py

To run it on a small cluster, I start the master and a worker first:

    spark-submit --master spark://localhost:7077 --executor-memory 1g --total-executor-cores 2 batch_job.py

I check the Spark UI on port 8080 for the cluster, or 4040 while a local job is running.

## Schedule

I scheduled it to run every day at 02:00 with cron:

    0 2 * * * cd ~/batch-project && spark-submit batch_job.py >> job.log 2>&1

## When something fails

I log the error with the full stack trace and the job exits with code 1, so cron or any scheduler can see the failure. Bad data does not stop the job, it ends up in the quarantine folder.
