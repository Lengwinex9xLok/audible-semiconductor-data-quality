"""Cash/share arithmetic for the frozen v10 annual cost scenarios.

This module has no file, database or network access. The normalized passive
wealth path is used as a price proxy, exactly as in the original v10 replay.
"""

import math
from typing import NamedTuple, Sequence

TOL = 1e-12


class Sleeve(NamedTuple):
    """One stock's period-start weight, passive wealth path and active positions."""

    weight: float
    prices: list[float]
    positions: list[float]


def require_close(actual: float, expected: float, label: str) -> None:
    """Reject nonfinite values as well as differences above the fixed tolerance."""
    if (
        not math.isfinite(actual)
        or not math.isfinite(expected)
        or abs(actual - expected) > TOL
    ):
        raise ValueError(f'{label}: {actual!r} differs from {expected!r}')


def sleeve_wealth(
    prices: Sequence[float], positions: Sequence[float], bps: float
) -> tuple[list[float], int, int]:
    """Return interval-end wealth and buy/sell counts, including liquidation.

    A buy funded by cash invests cash/(1+rate); a sale receives value*(1-rate).
    Consecutive active intervals keep shares and do not incur another round trip.
    Cash starts at one, earns zero yield and stays within its original sleeve.
    """
    rate = float(bps) / 10000
    if not math.isfinite(rate) or not 0 <= rate < 1:
        raise ValueError('Invalid one-way cost')
    if len(prices) < 2 or len(positions) != len(prices) - 1:
        raise ValueError('Price/interval lengths differ')
    if any(not math.isfinite(price) or price <= 0 for price in prices):
        raise ValueError('Invalid price; legitimate exits require a separate event engine')
    if any(position not in (0, 1) for position in positions):
        raise ValueError('Invalid position')

    cash, shares = 1.0, 0.0
    values = [1.0]
    buys = sells = 0

    for index, held in enumerate(positions):
        if held and shares == 0:
            shares = cash / (prices[index] * (1 + rate))
            cash = 0.0
            buys += 1

        if not held and shares != 0:
            raise ValueError('Open shares in a cash interval')

        final_interval = index == len(positions) - 1
        if held and (final_interval or positions[index + 1] == 0):
            cash = shares * prices[index + 1] * (1 - rate)
            shares = 0.0
            sells += 1

        value = cash + shares * prices[index + 1]
        if not math.isfinite(value) or value <= 0:
            raise ValueError('Invalid wealth')
        values.append(value)

    return values, buys, sells


def portfolio_return(
    sleeves: Sequence[Sleeve], bps: float, active: bool
) -> tuple[float, int, int]:
    """Aggregate final sleeve wealth using fixed period-start capital weights."""
    total, buys, sells = 0.0, 0, 0
    for weight, prices, positions in sleeves:
        selected_positions = positions if active else [1] * (len(prices) - 1)
        path, sleeve_buys, sleeve_sells = sleeve_wealth(prices, selected_positions, bps)
        total += weight * path[-1]
        buys += sleeve_buys
        sells += sleeve_sells
    return total - 1, buys, sells
