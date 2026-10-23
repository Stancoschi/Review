# Kafka and Spark streaming practice

I wanted to try the basic streaming pieces: a message broker (Kafka), a producer and a consumer, and Spark Structured Streaming reading from Kafka.

## What is in here

- `producer.py` - sends fake orders to the `orders` topic and some payments to the `payments` topic. Every 10th order has a bad amount on purpose.
- `consumer.py` - reads a topic and prints partition, offset and the message.
- `stream_job.py` - Spark Structured Streaming job with three modes:
  - `stateless`: parse the JSON, filter out bad amounts, keep only some columns
  - `windowed`: total and count per customer in 1 minute windows (with a watermark)
  - `joined`: joins orders with their payments (stream to stream join)
- `sqlite_sink.py` - my own sink: it writes each micro-batch into a SQLite table. It skips batches it has already written, so a restart does not create duplicates.
- `tuning/` - the producer performance test I ran with different settings, plus my notes.

## Setting up Kafka (no root needed)

I need Java 17 or newer. I download Kafka from kafka.apache.org, extract it, then:

    cd kafka
    KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
    bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
    bin/kafka-server-start.sh config/server.properties

In another terminal I create the topics:

    bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders --partitions 3 --replication-factor 1
    bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic payments --partitions 3 --replication-factor 1

## Running it

    pip install -r requirements.txt
    python consumer.py orders            # terminal 1
    python producer.py 30 0.5            # terminal 2

Spark needs the Kafka package. The version has to match my PySpark version (4.0.0):

    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 stream_job.py stateless
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 stream_job.py windowed
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 stream_job.py joined
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 sqlite_sink.py

(The first run downloads the package, so it needs internet.)

To check the custom sink, I run `sqlite3 orders_sink.db "select count(*) from orders"`. I can stop the job, start it again and the count stays correct.

## How it handles failures

Spark saves the Kafka offsets in the checkpoint folder. If the job stops, it continues from there. Because a batch can be replayed, the SQLite sink saves the batch id together with the data and ignores a batch it already has.

## Limits

I ran everything on one machine with one Kafka broker. The sink is a simple Spark `foreachBatch` sink, not a full Kafka Connect connector.
