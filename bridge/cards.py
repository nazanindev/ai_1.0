from __future__ import annotations
import random
from enum import IntEnum
from typing import Dict, List, Optional


class Suit(IntEnum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def symbol(self) -> str:
        return {
            Suit.CLUBS: "♣",
            Suit.DIAMONDS: "♦",
            Suit.HEARTS: "♥",
            Suit.SPADES: "♠",
        }[self]

    def name_str(self) -> str:
        return self.name.capitalize()

    def is_red(self) -> bool:
        return self in (Suit.DIAMONDS, Suit.HEARTS)


class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def symbol(self) -> str:
        return {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "T",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A",
        }[self]

    def hcp(self) -> int:
        return {
            Rank.ACE: 4,
            Rank.KING: 3,
            Rank.QUEEN: 2,
            Rank.JACK: 1,
        }.get(self, 0)


class Card:
    __slots__ = ("rank", "suit")

    def __init__(self, rank: Rank, suit: Suit) -> None:
        self.rank = rank
        self.suit = suit

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other: Card) -> bool:
        return (self.suit, self.rank) < (other.suit, other.rank)

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def __repr__(self) -> str:
        return f"{self.rank.symbol()}{self.suit.symbol()}"

    def hcp(self) -> int:
        return self.rank.hcp()


class Deck:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._cards: List[Card] = [
            Card(rank, suit)
            for suit in Suit
            for rank in Rank
        ]

    def shuffle(self) -> None:
        self._rng.shuffle(self._cards)

    def deal(self) -> Dict[str, List[Card]]:
        self.shuffle()
        seats = ["N", "E", "S", "W"]
        hands: Dict[str, List[Card]] = {s: [] for s in seats}
        for i, card in enumerate(self._cards):
            hands[seats[i % 4]].append(card)
        for hand in hands.values():
            hand.sort(key=lambda c: (c.suit, c.rank), reverse=True)
        return hands
