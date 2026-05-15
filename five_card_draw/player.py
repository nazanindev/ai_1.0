from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from five_card_draw.cards import Card


class Player:
    def __init__(self, name: str, chips: int, is_human: bool = False) -> None:
        self.name = name
        self.chips = chips
        self.is_human = is_human
        self.hand: list[Card] = []
        self.current_bet = 0
        self.total_bet = 0
        self.folded = False
        self.all_in = False

    def bet(self, amount: int) -> int:
        """Commit `amount` chips as a bet. Returns the actual amount bet."""
        actual = min(amount, self.chips)
        self.chips -= actual
        self.current_bet += actual
        self.total_bet += actual
        if self.chips == 0:
            self.all_in = True
        return actual

    def fold(self) -> None:
        self.folded = True

    def reset_for_hand(self) -> None:
        self.hand = []
        self.current_bet = 0
        self.total_bet = 0
        self.folded = False
        self.all_in = False

    def reset_for_street(self) -> None:
        self.current_bet = 0

    def is_active(self) -> bool:
        return not self.folded and not self.all_in

    def discard(self, indices: list[int]) -> list[Card]:
        """Remove cards at the given 0-based indices. Returns the removed cards."""
        indices_set = set(indices)
        removed = [self.hand[i] for i in sorted(indices_set)]
        self.hand = [c for i, c in enumerate(self.hand) if i not in indices_set]
        return removed

    def __repr__(self) -> str:
        return f"Player({self.name}, chips={self.chips})"
