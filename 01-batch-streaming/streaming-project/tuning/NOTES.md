# Broker tuning notes

I ran `tuning/perf_test.sh` on my own machine. The raw output is in `tuning/results.txt`.
I copy the numbers into this table after each run (the table is empty until I do).

| Run | Settings | records/sec | avg latency (ms) | max latency (ms) |
|---|---|---|---|---|
| 1 | defaults, acks=1 | | | |
| 2 | batch.size=65536, linger.ms=10, lz4 | | | |
| 3 | batch.size=131072, linger.ms=50, zstd | | | |
| 4 | same as 2 but acks=all | | | |
| 5 | same as 2, topic with 3 partitions | | | |

## What I changed and why

- `batch.size` and `linger.ms`: the producer waits a little so it can send more messages in one request. Usually more throughput, a bit more latency.
- `compression.type`: less data over the network and on disk, a little more CPU.
- `acks`: `acks=all` waits for all in-sync replicas. It is safer, but slower. With one broker the difference is small, so I only note it.
- Partitions: more partitions lets more consumers in the same group read in parallel.

## Scaling

On one machine I scaled by adding partitions (`kafka-topics.sh --alter --partitions 3`) and by starting 2 or 3 copies of `consumer.py` with the same group id. `kafka-consumer-groups.sh --describe --group demo-group` shows which consumer got which partition.
I did not add a second broker, because that needs a second config and a separate data folder.

## What to say if asked

The tuning is on the producer side and on the topic. I measured before and after with the same test, and I wrote down what got better and what got worse (see the table).
