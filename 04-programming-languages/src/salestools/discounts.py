"""Discounts with the Strategy pattern.

The discount rule changes (none, percent, threshold) but the code that adds up
the totals does not, so each rule is a small class with the same apply() method.
get_discount() picks one by name (a simple factory).
"""


class NoDiscount:
    def apply(self, amount):
        return amount


class PercentDiscount:
    def __init__(self, percent):
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def apply(self, amount):
        return amount * (1 - self.percent / 100)


class ThresholdDiscount:
    """Take a fixed amount off orders above a threshold."""

    def __init__(self, threshold, off):
        self.threshold = threshold
        self.off = off

    def apply(self, amount):
        return amount - self.off if amount > self.threshold else amount


RULES = {"none": NoDiscount, "percent": PercentDiscount, "threshold": ThresholdDiscount}


def get_discount(name, **options):
    if name not in RULES:
        raise ValueError(f"unknown discount: {name!r}")
    return RULES[name](**options)


def total_after_discount(amounts, discount):
    return round(sum(discount.apply(a) for a in amounts), 2)
