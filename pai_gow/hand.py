from __future__ import annotations
from typing import Optional
from .tiles import Tile, PAIR_RANKING


class Hand:
    """Two-tile Pai Gow hand."""

    def __init__(self, t1: Tile, t2: Tile) -> None:
        self.tiles: tuple[Tile, Tile] = (t1, t2)

    # ------------------------------------------------------------------
    # Pair detection
    # ------------------------------------------------------------------

    def is_pair(self) -> bool:
        t1, t2 = self.tiles
        return t1.pair_name == t2.pair_name

    def pair_name(self) -> Optional[str]:
        return self.tiles[0].pair_name if self.is_pair() else None

    def pair_rank_index(self) -> Optional[int]:
        """Lower index = stronger pair."""
        pn = self.pair_name()
        if pn is None:
            return None
        try:
            return PAIR_RANKING.index(pn)
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Hand value (pip sum mod 10, with Gee Joon wild)
    # ------------------------------------------------------------------

    def _gee_joon_value(self, gj_tile: Tile, other: Tile) -> int:
        # Gee Joon tile can count as 3 or 6 — pick whichever gives higher hand value.
        return max((3 + other.total) % 10, (6 + other.total) % 10)

    def value(self) -> int:
        if self.is_pair():
            # Pairs are compared by rank, not value; return canonical pip sum mod 10.
            return (self.tiles[0].total + self.tiles[1].total) % 10

        t1, t2 = self.tiles
        gj_names = {"GeeJoon-A", "GeeJoon-B"}
        if t1.name in gj_names and t2.name not in gj_names:
            return self._gee_joon_value(t1, t2)
        if t2.name in gj_names and t1.name not in gj_names:
            return self._gee_joon_value(t2, t1)

        return (t1.total + t2.total) % 10

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def _beats(self, other: Hand) -> Optional[bool]:
        """Return True if self beats other, False if other beats self, None for tie."""
        s_pair = self.is_pair()
        o_pair = other.is_pair()

        if s_pair and not o_pair:
            return True
        if not s_pair and o_pair:
            return False

        if s_pair and o_pair:
            s_idx = self.pair_rank_index()
            o_idx = other.pair_rank_index()
            if s_idx < o_idx:
                return True
            if s_idx > o_idx:
                return False
            return None  # same pair (shouldn't happen in 32-tile deck for most pairs)

        # Both non-pair: compare by value
        s_val = self.value()
        o_val = other.value()
        if s_val > o_val:
            return True
        if s_val < o_val:
            return False
        return None  # tie — banker wins ties

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        result = self._beats(other)
        return result is True

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        result = other._beats(self)
        return result is True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        return self._beats(other) is None

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        t1, t2 = self.tiles
        pair_tag = f" ({self.pair_name()} pair!)" if self.is_pair() else f" = {self.value()}"
        return f"{t1}  {t2}{pair_tag}"
