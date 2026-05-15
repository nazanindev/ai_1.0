from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Tile:
    name: str
    pips: tuple[int, int]      # (top_half, bottom_half)
    chinese: str               # display character
    civil_rank: Optional[int]  # 1=highest civil, None=military
    pair_name: str             # canonical pair group this tile belongs to

    @property
    def total(self) -> int:
        return self.pips[0] + self.pips[1]

    def __str__(self) -> str:
        return f"[{self.pips[0]}:{self.pips[1]}]"


# ---------------------------------------------------------------------------
# The 32-tile Pai Gow set
# Civil tiles: 11 matched pairs (each tile appears twice), civil_rank 1-11
# Military tiles: 10 tiles forming 5 "mixed" pairs (mismatched pips, same rank)
#   Gee Joon is a special military pair that acts as the highest pair overall.
# ---------------------------------------------------------------------------

TILE_SET: list[Tile] = [
    # --- Civil pairs (each tile listed twice) ---
    # Rank 1: Teen (天, 12 pips — 6+6)
    Tile("Teen",  (6, 6), "天", 1,  "Teen"),
    Tile("Teen",  (6, 6), "天", 1,  "Teen"),
    # Rank 2: Day (地, 2 pips — 1+1)
    Tile("Day",   (1, 1), "地", 2,  "Day"),
    Tile("Day",   (1, 1), "地", 2,  "Day"),
    # Rank 3: Yan (人, 8 pips — 4+4)
    Tile("Yan",   (4, 4), "人", 3,  "Yan"),
    Tile("Yan",   (4, 4), "人", 3,  "Yan"),
    # Rank 4: Gor (鹅, 4 pips — 1+3)
    Tile("Gor",   (1, 3), "鹅", 4,  "Gor"),
    Tile("Gor",   (1, 3), "鹅", 4,  "Gor"),
    # Rank 5: Mooy (梅, 6 pips — 1+5)
    Tile("Mooy",  (1, 5), "梅", 5,  "Mooy"),
    Tile("Mooy",  (1, 5), "梅", 5,  "Mooy"),
    # Rank 6: Chong (长, 11 pips — 5+6)
    Tile("Chong", (5, 6), "长", 6,  "Chong"),
    Tile("Chong", (5, 6), "长", 6,  "Chong"),
    # Rank 7: Bon (板, 10 pips — 4+6)
    Tile("Bon",   (4, 6), "板", 7,  "Bon"),
    Tile("Bon",   (4, 6), "板", 7,  "Bon"),
    # Rank 8: Foo (斧, 7 pips — 1+6)
    Tile("Foo",   (1, 6), "斧", 8,  "Foo"),
    Tile("Foo",   (1, 6), "斧", 8,  "Foo"),
    # Rank 9: Ping (屏, 8 pips — 2+6)
    Tile("Ping",  (2, 6), "屏", 9,  "Ping"),
    Tile("Ping",  (2, 6), "屏", 9,  "Ping"),
    # Rank 10: Tit (黑七, 7 pips — 2+5)
    Tile("Tit",   (2, 5), "七", 10, "Tit"),
    Tile("Tit",   (2, 5), "七", 10, "Tit"),
    # Rank 11: Look (虎, 9 pips — 3+6)
    Tile("Look",  (3, 6), "虎", 11, "Look"),
    Tile("Look",  (3, 6), "虎", 11, "Look"),

    # --- Military tiles (mismatched pairs) ---
    # Gee Joon: highest pair — 3+6 and 2+4 tiles (count as 3 or 6 in hands)
    Tile("GeeJoon-A", (2, 4), "喜", None, "GeeJoon"),
    Tile("GeeJoon-B", (1, 2), "喜", None, "GeeJoon"),
    # Mixed 9: 1+8 and 4+5
    Tile("Mix9-A",    (1, 8), "九", None, "Mix9"),
    Tile("Mix9-B",    (4, 5), "九", None, "Mix9"),
    # Mixed 8: 3+5 and 2+6
    Tile("Mix8-A",    (3, 5), "八", None, "Mix8"),
    Tile("Mix8-B",    (2, 6), "八", None, "Mix8"),  # note: 2+6 pip count same as Ping civil
    # Mixed 7: 1+6 and 2+5  — same pip counts as Foo and Tit civil tiles
    Tile("Mix7-A",    (1, 6), "七", None, "Mix7"),
    Tile("Mix7-B",    (2, 5), "七", None, "Mix7"),
    # Mixed 5: 1+4 and 2+3
    Tile("Mix5-A",    (1, 4), "五", None, "Mix5"),
    Tile("Mix5-B",    (2, 3), "五", None, "Mix5"),
]

assert len(TILE_SET) == 32, f"Expected 32 tiles, got {len(TILE_SET)}"


# Pair ranking: highest to lowest (index 0 = highest)
# Civil pairs are ranked by civil_rank within their category;
# military "mixed" pairs are ranked below all civil pairs except they beat nothing.
# Gee Joon is the supreme pair (beats everything).
PAIR_RANKING: list[str] = [
    "GeeJoon",  # highest pair of all
    "Teen",     # civil rank 1
    "Day",      # civil rank 2
    "Yan",      # civil rank 3
    "Gor",      # civil rank 4
    "Mooy",     # civil rank 5
    "Chong",    # civil rank 6
    "Bon",      # civil rank 7
    "Foo",      # civil rank 8
    "Ping",     # civil rank 9
    "Tit",      # civil rank 10
    "Look",     # civil rank 11
    "Mix9",     # military mixed 9
    "Mix8",     # military mixed 8
    "Mix7",     # military mixed 7
    "Mix5",     # military mixed 5
]


class Deck:
    def __init__(self) -> None:
        self._tiles: list[Tile] = list(TILE_SET)
        random.shuffle(self._tiles)

    def draw(self) -> Tile:
        if not self._tiles:
            raise RuntimeError("Deck is empty")
        return self._tiles.pop()

    def __len__(self) -> int:
        return len(self._tiles)
