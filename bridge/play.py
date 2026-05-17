from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from bridge.bidding import Bid, PARTNERSHIPS, Strain
from bridge.cards import Card, Suit


@dataclass
class Trick:
    trump: Optional[Suit]  # None for NT
    lead_seat: str
    plays: List[Tuple[str, Card]] = field(default_factory=list)

    @property
    def lead_suit(self) -> Optional[Suit]:
        return self.plays[0][1].suit if self.plays else None

    @property
    def is_complete(self) -> bool:
        return len(self.plays) == 4

    def winner(self) -> str:
        assert self.is_complete
        lead_suit = self.plays[0][1].suit
        best_seat, best_card = self.plays[0]
        for seat, card in self.plays[1:]:
            if _beats(card, best_card, lead_suit, self.trump):
                best_seat, best_card = seat, card
        return best_seat

    def winning_card(self) -> Card:
        assert self.is_complete
        lead_suit = self.plays[0][1].suit
        _, best_card = self.plays[0]
        for _, card in self.plays[1:]:
            if _beats(card, best_card, lead_suit, self.trump):
                best_card = card
        return best_card


def _beats(card: Card, current_best: Card, lead_suit: Suit, trump: Optional[Suit]) -> bool:
    if trump is not None:
        if card.suit == trump and current_best.suit != trump:
            return True
        if card.suit != trump and current_best.suit == trump:
            return False
    if card.suit == current_best.suit:
        return card.rank > current_best.rank
    return False


def legal_plays(hand: List[Card], trick: Trick) -> List[Card]:
    lead_suit = trick.lead_suit
    if lead_suit is None or not trick.plays:
        return list(hand)
    followers = [c for c in hand if c.suit == lead_suit]
    return followers if followers else list(hand)


def simple_ai_play(hand: List[Card], trick: Trick, bid: Bid) -> Card:
    legal = legal_plays(hand, trick)

    trump_suit = bid.strain.as_suit()

    # On lead (first to play in trick)
    if not trick.plays:
        return _lead_card(hand, trump_suit)

    lead_suit = trick.lead_suit
    partner_seat = None
    if len(trick.plays) >= 2:
        # Determine which seat is partner
        from bridge.bidding import PARTNERS
        current_idx = len(trick.plays)
        seats_order = _seats_from(trick.lead_seat)
        partner_seat = seats_order[2] if current_idx >= 3 else None

    # Check if partner is currently winning
    if len(trick.plays) >= 2 and partner_seat:
        current_winner = _current_winner(trick, trump_suit)
        partner_winning = current_winner == partner_seat

        if partner_winning:
            # Play lowest card that follows suit
            return _lowest_card(legal)

    # Try to win the trick cheaply
    winning = [c for c in legal if _would_win(c, trick, trump_suit)]
    if winning:
        return min(winning, key=lambda c: c.rank)

    # Cannot win — play lowest
    return _lowest_card(legal)


def _seats_from(lead: str) -> List[str]:
    from bridge.bidding import SEATS
    idx = SEATS.index(lead)
    return [SEATS[(idx + i) % 4] for i in range(4)]


def _current_winner(trick: Trick, trump: Optional[Suit]) -> str:
    best_seat, best_card = trick.plays[0]
    lead_suit = trick.plays[0][1].suit
    for seat, card in trick.plays[1:]:
        if _beats(card, best_card, lead_suit, trump):
            best_seat, best_card = seat, card
    return best_seat


def _would_win(card: Card, trick: Trick, trump: Optional[Suit]) -> bool:
    if not trick.plays:
        return True
    lead_suit = trick.plays[0][1].suit
    for _, existing in trick.plays:
        if not _beats(card, existing, lead_suit, trump):
            return False
    return True


def _lowest_card(hand: List[Card]) -> Card:
    return min(hand, key=lambda c: c.rank)


def _lead_card(hand: List[Card], trump: Optional[Suit]) -> Card:
    # Lead longest non-trump suit, top of sequence
    by_suit: Dict[Suit, List[Card]] = {}
    for c in hand:
        by_suit.setdefault(c.suit, []).append(c)

    # Prefer long non-trump suits
    candidates = {s: cards for s, cards in by_suit.items() if s != trump}
    if not candidates:
        candidates = by_suit

    best_suit = max(candidates, key=lambda s: (len(candidates[s]), int(s)))
    suit_cards = sorted(candidates[best_suit], key=lambda c: c.rank, reverse=True)
    return suit_cards[0]
