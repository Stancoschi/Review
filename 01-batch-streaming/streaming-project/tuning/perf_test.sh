#!/usr/bin/env bash
# Runs the same producer test with different settings and saves the output.
# usage: KAFKA_HOME=~/kafka bash tuning/perf_test.sh
set -e
KAFKA_HOME=${KAFKA_HOME:-$HOME/kafka}
BROKER=localhost:9092
RECORDS=200000
SIZE=1024

$KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BROKER --create --if-not-exists \
  --topic perf --partitions 1 --replication-factor 1

run() {
  name=$1; shift
  echo "=== $name ===" | tee -a tuning/results.txt
  $KAFKA_HOME/bin/kafka-producer-perf-test.sh --topic perf --num-records $RECORDS \
    --record-size $SIZE --throughput -1 --producer-props bootstrap.servers=$BROKER "$@" \
    | tail -1 | tee -a tuning/results.txt
}

run "1 default"            acks=1
run "2 batch+linger+lz4"   acks=1 batch.size=65536 linger.ms=10 compression.type=lz4
run "3 bigger batch+zstd"  acks=1 batch.size=131072 linger.ms=50 compression.type=zstd
run "4 acks=all"           acks=all batch.size=65536 linger.ms=10 compression.type=lz4

# more partitions, same test as run 2
$KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BROKER --alter --topic perf --partitions 3
run "5 three partitions"   acks=1 batch.size=65536 linger.ms=10 compression.type=lz4
