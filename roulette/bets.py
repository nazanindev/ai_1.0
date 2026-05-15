from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .wheel import Pocket


@dataclass
class Bet:
    kind: str      # 'straight' | 'color' | 'parity' | 'half' | 'dozen' | 'column'
    value: Any     # int for straight; str for others
    amount: int


def resolve(bet: Bet, pocket: Pocket) -> int:
    """Return net winnings (positive) or loss (-bet.amount) for a pocket."""
    n = pocket.number
    won = False

    if bet.kind == "straight":
        won = n == int(bet.value)
        payout_mult = 35
    elif bet.kind == "color":
        won = pocket.color == bet.value
        payout_mult = 1
    elif bet.kind == "parity":
        if n == 0:
            won = False
        elif bet.value == "even":
            won = n % 2 == 0
        else:
            won = n % 2 == 1
        payout_mult = 1
    elif bet.kind == "half":
        if n == 0:
            won = False
        elif bet.value == "low":
            won = 1 <= n <= 18
        else:
            won = 19 <= n <= 36
        payout_mult = 1
    elif bet.kind == "dozen":
        if n == 0:
            won = False
        else:
            dozen = (n - 1) // 12 + 1
            won = dozen == int(bet.value)
        payout_mult = 2
    elif bet.kind == "column":
        if n == 0:
            won = False
        else:
            col = (n - 1) % 3 + 1
            won = col == int(bet.value)
        payout_mult = 2
    else:
        raise ValueError(f"Unknown bet kind: {bet.kind!r}")

    if won:
        return bet.amount * payout_mult
    return -bet.amount
