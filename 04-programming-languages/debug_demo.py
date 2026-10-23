"""Debugging exercise: logging + breakpoint.

Run it, then uncomment breakpoint() and step through with pdb:
n = next line, p variable = print, c = continue, q = quit
"""

import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-7s %(message)s")
log = logging.getLogger("debug_demo")


def average(rows):
    total = 0
    for row in rows:
        # breakpoint()
        total += row["amount"]
    return total / len(rows)  # BUG: crashes when an amount is None


def average_fixed(rows):
    amounts = [r["amount"] for r in rows if r["amount"] is not None]
    log.debug("using %s of %s rows", len(amounts), len(rows))
    return sum(amounts) / len(amounts) if amounts else None


if __name__ == "__main__":
    data = [{"amount": 10}, {"amount": 20}, {"amount": None}]
    try:
        log.info("average = %s", average(data))
    except TypeError:
        log.exception("average() crashed")
    log.info("fixed average = %s", average_fixed(data))
