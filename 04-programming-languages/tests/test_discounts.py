import pytest

from salestools.discounts import (
    NoDiscount,
    PercentDiscount,
    ThresholdDiscount,
    get_discount,
    total_after_discount,
)


@pytest.mark.parametrize(
    "discount, amount, expected",
    [
        (NoDiscount(), 100, 100),
        (PercentDiscount(10), 100, 90),
        (ThresholdDiscount(50, 5), 100, 95),
        (ThresholdDiscount(50, 5), 50, 50),
    ],
)
def test_apply(discount, amount, expected):
    assert discount.apply(amount) == pytest.approx(expected)


def test_percent_out_of_range():
    with pytest.raises(ValueError):
        PercentDiscount(101)


def test_factory_and_total():
    assert isinstance(get_discount("none"), NoDiscount)
    assert total_after_discount([100, 50], get_discount("percent", percent=10)) == 135
    with pytest.raises(ValueError):
        get_discount("black-friday")
