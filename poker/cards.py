from __future__ import annotations
import random
from enum import Enum


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Rank(Enum):
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")

    def __init__(self, value: int, symbol: str) -> None:
        self._value_ = value
        self.symbol = symbol

    def __lt__(self, other: Rank) -> bool:
        return self.value < other.value


# ANSI color codes
_RED = "\033[91m"
_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"


def _suit_color(suit: Suit) -> str:
    return _RED if suit in (Suit.HEARTS, Suit.DIAMONDS) else ""


class Card:
    def __init__(self, rank: Rank, suit: Suit) -> None:
        self.rank = rank
        self.suit = suit

    def __repr__(self) -> str:
        return f"{self.rank.symbol}{self.suit.value}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def colored_str(self) -> str:
        color = _suit_color(self.suit)
        return f"{color}{self.rank.symbol}{self.suit.value}{_RESET}"

    def render_lines(self, hidden: bool = False) -> list[str]:
        """Return 5 lines of card art (width 7 chars each)."""
        if hidden:
            return [
                "┌─────┐",
                "│░░░░░│",
                "│░░░░░│",
                "│░░░░░│",
                "└─────┘",
            ]
        color = _suit_color(self.suit)
        rank_s = self.rank.symbol.ljust(2)
        suit_s = self.suit.value
        return [
            "┌─────┐",
            f"│{color}{rank_s}{_RESET}   │",
            f"│  {color}{suit_s}{_RESET}  │",
            f"│   {color}{rank_s.rstrip().rjust(2)}{_RESET}│",
            "└─────┘",
        ]


class Deck:
    def __init__(self) -> None:
        self._cards: list[Card] = [
            Card(rank, suit) for suit in Suit for rank in Rank
        ]

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def deal(self) -> Card:
        if not self._cards:
            raise RuntimeError("Deck is empty")
        return self._cards.pop()

    def __len__(self) -> int:
        return len(self._cards)
