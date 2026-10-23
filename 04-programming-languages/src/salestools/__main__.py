"""Run with:  python -m salestools data/sales.csv"""

import logging
import sys

from salestools.cleaning import clean_rows
from salestools.report import read_csv, save_gz, summarize

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

good, bad = clean_rows(read_csv(sys.argv[1]))
save_gz({"good": good, "bad": bad}, "out/clean.json.gz")
print(summarize([row["amount"] for row in good]))
print(f"good={len(good)} bad={len(bad)}")
