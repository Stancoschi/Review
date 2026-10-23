"""The network is replaced in these tests.

stub: fetch_rates is replaced by a fake that returns fixed rates
mock: urlopen is replaced by a Mock so I can check how it was called
"""

import io
import json
from unittest.mock import MagicMock, patch

import pytest

from salestools import rates


def test_same_currency_does_not_call_network():
    with patch("salestools.rates.fetch_rates") as fake:
        assert rates.to_ron(10, "RON") == 10
    fake.assert_not_called()


def test_stubbed_rates():
    with patch("salestools.rates.fetch_rates", return_value={"EUR": 5.0}):
        assert rates.to_ron(10, "EUR") == 50.0
        with pytest.raises(ValueError):
            rates.to_ron(10, "USD")


def test_fetch_rates_reads_json():
    fake_urlopen = MagicMock()
    fake_urlopen.return_value.__enter__.return_value = io.StringIO(
        json.dumps({"EUR": 4.97})
    )
    with patch("salestools.rates.urllib.request.urlopen", fake_urlopen):
        assert rates.fetch_rates("http://test/r", timeout=1) == {"EUR": 4.97}
    fake_urlopen.assert_called_once_with("http://test/r", timeout=1)
