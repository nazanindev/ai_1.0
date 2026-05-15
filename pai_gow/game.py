from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from typing import Optional
from .tiles import Tile, Deck
from .hand import Hand


@dataclass
class RoundResult:
    outcome: str        # 'win' | 'push' | 'lose'
    payout: int         # net change to bankroll (positive = gain, negative = loss)
    player_high: Hand
    player_low: Hand
    banker_high: Hand
    banker_low: Hand


class Game:
    def __init__(self, bankroll: int = 1000) -> None:
        self.bankroll = bankroll
        self._deck: Optional[Deck] = None

    def _fresh_deck(self) -> Deck:
        self._deck = Deck()
        return self._deck

    def deal(self) -> tuple[list[Tile], list[Tile]]:
        """Return (player_tiles, banker_tiles), 4 tiles each from a fresh shuffle."""
        deck = self._fresh_deck()
        player = [deck.draw() for _ in range(4)]
        banker = [deck.draw() for _ in range(4)]
        return player, banker

    # ------------------------------------------------------------------
    # House-way banker AI
    # ------------------------------------------------------------------

    def house_way_split(self, tiles: list[Tile]) -> tuple[Hand, Hand]:
        """
        Banker follows the house way: try every legal split and pick the one that
        maximises the high hand first, then the low hand — a greedy approach that
        mirrors standard casino house-way heuristics.

        A split is legal when high >= low (front hand must not beat back hand).
        """
        best: Optional[tuple[Hand, Hand]] = None

        for idx in combinations(range(4), 2):
            hi_tiles = [tiles[i] for i in idx]
            lo_tiles = [tiles[i] for i in range(4) if i not in idx]
            h_high = Hand(hi_tiles[0], hi_tiles[1])
            h_low  = Hand(lo_tiles[0], lo_tiles[1])

            # Ensure high >= low (back hand must be stronger or equal to front)
            if h_low > h_high:
                h_high, h_low = h_low, h_high

            if best is None:
                best = (h_high, h_low)
                continue

            b_high, b_low = best
            # Prefer the split with the stronger high hand; break ties on low hand
            if h_high > b_high or (h_high == b_high and h_low > b_low):
                best = (h_high, h_low)

        assert best is not None
        return best

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_split(
        self,
        tiles: list[Tile],
        high: Hand,
        low: Hand,
    ) -> Optional[str]:
        """
        Return an error message if the split is illegal, else None.
        Rules: the two hands must use exactly the 4 dealt tiles, and the
        high (back) hand must be >= the low (front) hand.
        """
        used = list(high.tiles) + list(low.tiles)
        if sorted(id(t) for t in used) != sorted(id(t) for t in tiles):
            return "The two hands must use all four of your dealt tiles."
        if low > high:
            return (
                "Your front (low) hand cannot be stronger than your back (high) hand. "
                "Please re-split."
            )
        return None

    # ------------------------------------------------------------------
    # Settlement
    # ------------------------------------------------------------------

    def settle(
        self,
        bet: int,
        player_high: Hand,
        player_low: Hand,
        banker_high: Hand,
        banker_low: Hand,
    ) -> RoundResult:
        # Banker wins ties (standard casino rule)
        p_wins_high = player_high > banker_high
        p_wins_low  = player_low  > banker_low

        if p_wins_high and p_wins_low:
            # Player wins both — house takes 5% commission (rounded down)
            gross = bet
            commission = max(0, gross // 20)  # 5%
            payout = gross - commission
            outcome = 'win'
        elif not p_wins_high and not p_wins_low:
            payout = -bet
            outcome = 'lose'
        else:
            payout = 0
            outcome = 'push'

        self.bankroll += payout
        return RoundResult(
            outcome=outcome,
            payout=payout,
            player_high=player_high,
            player_low=player_low,
            banker_high=banker_high,
            banker_low=banker_low,
        )
