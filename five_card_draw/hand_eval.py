from __future__ import annotations
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from five_card_draw.cards import Card

# Hand rank categories (higher = better)
HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8
ROYAL_FLUSH = 9

_CATEGORY_NAMES = {
    HIGH_CARD: "High Card",
    ONE_PAIR: "One Pair",
    TWO_PAIR: "Two Pair",
    THREE_OF_A_KIND: "Three of a Kind",
    STRAIGHT: "Straight",
    FLUSH: "Flush",
    FULL_HOUSE: "Full House",
    FOUR_OF_A_KIND: "Four of a Kind",
    STRAIGHT_FLUSH: "Straight Flush",
    ROYAL_FLUSH: "Royal Flush",
}


def _score_five(cards: list[Card]) -> tuple:
    """Score exactly 5 cards. Returns a comparable tuple (category, ...)."""
    values = sorted((c.rank.value for c in cards), reverse=True)
    suits = [c.suit for c in cards]
    counts = Counter(values)
    is_flush = len(set(suits)) == 1

    # Straight detection (including wheel A-2-3-4-5)
    unique_vals = sorted(set(values), reverse=True)
    is_straight = False
    straight_high = 0
    if len(unique_vals) == 5:
        if unique_vals[0] - unique_vals[4] == 4:
            is_straight = True
            straight_high = unique_vals[0]
        elif unique_vals == [14, 5, 4, 3, 2]:  # wheel
            is_straight = True
            straight_high = 5

    freq = sorted(counts.values(), reverse=True)
    most_common = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    ordered_vals = [v for v, _ in most_common]

    if is_straight and is_flush:
        if straight_high == 14:
            return (ROYAL_FLUSH,)
        return (STRAIGHT_FLUSH, straight_high)

    if freq[0] == 4:
        quad_val = ordered_vals[0]
        kicker = ordered_vals[1]
        return (FOUR_OF_A_KIND, quad_val, kicker)

    if freq[0] == 3 and freq[1] == 2:
        trip_val = ordered_vals[0]
        pair_val = ordered_vals[1]
        return (FULL_HOUSE, trip_val, pair_val)

    if is_flush:
        return (FLUSH, *values)

    if is_straight:
        return (STRAIGHT, straight_high)

    if freq[0] == 3:
        trip_val = ordered_vals[0]
        kickers = sorted(ordered_vals[1:], reverse=True)
        return (THREE_OF_A_KIND, trip_val, *kickers)

    if freq[0] == 2 and freq[1] == 2:
        pair1 = ordered_vals[0]
        pair2 = ordered_vals[1]
        kicker = ordered_vals[2]
        high_pair, low_pair = max(pair1, pair2), min(pair1, pair2)
        return (TWO_PAIR, high_pair, low_pair, kicker)

    if freq[0] == 2:
        pair_val = ordered_vals[0]
        kickers = sorted(ordered_vals[1:], reverse=True)
        return (ONE_PAIR, pair_val, *kickers)

    return (HIGH_CARD, *values)


def evaluate(cards: list[Card]) -> tuple[tuple, str]:
    """
    Evaluate exactly 5 cards.
    Returns (score_tuple, hand_name) where higher score_tuple means better hand.
    """
    if len(cards) != 5:
        raise ValueError(f"Need exactly 5 cards, got {len(cards)}")
    score = _score_five(cards)
    name = _CATEGORY_NAMES[score[0]]
    return score, name
