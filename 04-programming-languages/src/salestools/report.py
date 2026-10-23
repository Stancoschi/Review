"""Files and numbers: csv, gzip, json, pathlib, statistics."""

import csv
import gzip
import json
import statistics
from pathlib import Path


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_gz(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(data, handle, default=str)
    return path


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def summarize(amounts):
    if not amounts:
        raise ValueError("no amounts to summarize")
    return {
        "count": len(amounts),
        "total": round(sum(amounts), 2),
        "mean": round(statistics.mean(amounts), 2),
        "median": round(statistics.median(amounts), 2),
    }
