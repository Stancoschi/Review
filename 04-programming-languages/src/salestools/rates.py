"""Currency conversion. fetch_rates() uses the network, so tests replace it."""

import json
import urllib.request

URL = "https://example.com/rates.json"


def fetch_rates(url=URL, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def to_ron(amount, currency):
    if currency == "RON":
        return amount
    rates = fetch_rates()
    if currency not in rates:
        raise ValueError(f"no rate for {currency}")
    return round(amount * rates[currency], 2)
