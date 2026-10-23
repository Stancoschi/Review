"""Cleaning rows: amounts (regex), dates (datetime), whole rows."""

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

AMOUNT = re.compile(
    r"^\s*(-?\d+(?:[.,]\d{1,2})?)\s*(?:lei|ron|eur)?\s*$", re.IGNORECASE
)
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


class InvalidRowError(ValueError):
    """A value or a row that cannot be cleaned."""


def parse_amount(text):
    """'25,50 lei' -> 25.5 (must be a positive number)."""
    match = AMOUNT.match(str(text or ""))
    if not match:
        raise InvalidRowError(f"bad amount: {text!r}")
    value = float(match.group(1).replace(",", "."))
    if value <= 0:
        raise InvalidRowError(f"amount must be positive: {value}")
    return value


def parse_date(text):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(str(text).strip(), fmt).date()
        except ValueError:
            continue
    raise InvalidRowError(f"unknown date format: {text!r}")


def clean_row(row):
    try:
        order_id = int(row["order_id"])
    except (KeyError, ValueError) as err:
        raise InvalidRowError(f"bad order_id: {err}") from err
    return {
        "order_id": order_id,
        "category": row.get("category", "").strip().lower(),
        "amount": parse_amount(row.get("amount")),
        "date": parse_date(row.get("date")),
    }


def clean_rows(rows):
    """Return (good, bad). One bad row does not stop the others."""
    good, bad = [], []
    for number, row in enumerate(rows, start=1):
        try:
            good.append(clean_row(row))
        except InvalidRowError as err:
            logger.warning("row %s rejected: %s", number, err)
            bad.append({"row": number, "reason": str(err)})
    logger.info("%s good, %s bad", len(good), len(bad))
    return good, bad
