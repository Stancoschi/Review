# salestools

A small Python package I wrote to practice clean code, testing and packaging. It cleans sales rows (amounts and dates), writes a compressed report, applies discounts and converts currency.

## Files

- `src/salestools/cleaning.py` - parse amounts (regex) and dates (datetime), clean rows, own exception
- `src/salestools/report.py` - read CSV, write gzip JSON, summary with statistics
- `src/salestools/discounts.py` - discounts, Strategy pattern with a small factory
- `src/salestools/rates.py` - currency conversion that calls a web API
- `tests/` - pytest tests
- `debug_demo.py` - logging and breakpoint exercise
- `pyproject.toml` - metadata, dependencies, pytest and ruff settings

## Setup and run

    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    python -m salestools data/sales.csv

## Style

PEP 8: 4 spaces, snake_case, docstrings, lines up to 88 characters. Checked with `ruff check .`.

## Tests

    pytest

Shows missing lines and fails if coverage is under 90%. Tests are parameterized where the same logic has many inputs. Only `rates.py` uses the network, so its tests replace `fetch_rates` (stub) and `urlopen` (mock).

## Package

    pip install build && python -m build
    pip install dist/salestools-0.1.0-py3-none-any.whl     # in a new venv

## Why Strategy

The discount rule changes, but the code that adds the totals does not. Each rule is a class with `apply()`, so adding a new one means adding a class and one line in `RULES`.
