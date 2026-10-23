import pytest
from pyspark.sql import SparkSession
import batch_job


@pytest.fixture(scope="module")
def spark():
    s = SparkSession.builder.master("local[2]").getOrCreate()
    yield s
    s.stop()


def test_bad_rows_go_to_quarantine(spark):
    df = spark.createDataFrame(
        [(1, 10.0, 1), (2, -5.0, 1), (3, None, 2), (4, 7.0, None)],
        "id int, amount double, customer_id int")
    valid, rejected = batch_job.split_valid(df)
    assert valid.count() == 1
    assert rejected.count() == 3


def test_nested_json_is_flattened(spark):
    assert batch_job.read_orders(spark).count() == 4


def test_full_job(spark, tmp_path):
    n_in, n_valid, n_rej = batch_job.run(spark, str(tmp_path))
    assert (n_in, n_valid, n_rej) == (8, 5, 3)
