from datetime import date

import pytest

from salestools.cleaning import (
    InvalidRowError,
    clean_row,
    clean_rows,
    parse_amount,
    parse_date,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("25", 25.0),
        ("25,50 lei", 25.5),
        (" 10 RON ", 10.0),
        (80, 80.0),
    ],
)
def test_parse_amount_ok(text, expected):
    assert parse_amount(text) == expected


@pytest.mark.parametrize("text", [None, "", "abc", "-10", "0", "1.234"])
def test_parse_amount_bad(text):
    with pytest.raises(InvalidRowError):
        parse_amount(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("2026-10-01", date(2026, 10, 1)),
        ("02.10.2026", date(2026, 10, 2)),
        ("03/10/2026", date(2026, 10, 3)),
    ],
)
def test_parse_date_ok(text, expected):
    assert parse_date(text) == expected


def test_parse_date_bad():
    with pytest.raises(InvalidRowError):
        parse_date("yesterday")


def test_clean_row_bad_order_id():
    with pytest.raises(InvalidRowError):
        clean_row({"order_id": "x", "amount": "5", "date": "2026-10-01"})


def test_clean_rows_splits_good_and_bad():
    rows = [
        {"order_id": "1", "category": " Books ", "amount": "10", "date": "2026-10-01"},
        {"order_id": "2", "category": "toys", "amount": "abc", "date": "2026-10-01"},
    ]
    good, bad = clean_rows(rows)
    assert good[0]["category"] == "books"
    assert bad == [{"row": 2, "reason": "bad amount: 'abc'"}]
