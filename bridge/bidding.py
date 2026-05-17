from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Optional, Tuple

from bridge.cards import Card, Rank, Suit


class Strain(IntEnum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3
    NOTRUMP = 4

    def symbol(self) -> str:
        return {
            Strain.CLUBS: "♣",
            Strain.DIAMONDS: "♦",
            Strain.HEARTS: "♥",
            Strain.SPADES: "♠",
            Strain.NOTRUMP: "NT",
        }[self]

    def is_major(self) -> bool:
        return self in (Strain.HEARTS, Strain.SPADES)

    def is_minor(self) -> bool:
        return self in (Strain.CLUBS, Strain.DIAMONDS)

    def is_red(self) -> bool:
        return self in (Strain.DIAMONDS, Strain.HEARTS)

    def as_suit(self) -> Optional[Suit]:
        mapping = {
            Strain.CLUBS: Suit.CLUBS,
            Strain.DIAMONDS: Suit.DIAMONDS,
            Strain.HEARTS: Suit.HEARTS,
            Strain.SPADES: Suit.SPADES,
        }
        return mapping.get(self)


@dataclass(frozen=True)
class Bid:
    level: int  # 1–7
    strain: Strain

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 7:
            raise ValueError(f"Bid level must be 1–7, got {self.level}")

    def __lt__(self, other: Bid) -> bool:
        return (self.level, self.strain) < (other.level, other.strain)

    def __le__(self, other: Bid) -> bool:
        return (self.level, self.strain) <= (other.level, other.strain)

    def __str__(self) -> str:
        return f"{self.level}{self.strain.symbol()}"

    def tricks_needed(self) -> int:
        return self.level + 6


class CallType(Enum):
    PASS = "Pass"
    DOUBLE = "Dbl"
    REDOUBLE = "Rdbl"
    BID = "Bid"


@dataclass(frozen=True)
class Call:
    call_type: CallType
    bid: Optional[Bid] = None

    def __str__(self) -> str:
        if self.call_type == CallType.BID:
            return str(self.bid)
        return self.call_type.value

    @classmethod
    def pass_call(cls) -> Call:
        return cls(CallType.PASS)

    @classmethod
    def double(cls) -> Call:
        return cls(CallType.DOUBLE)

    @classmethod
    def redouble(cls) -> Call:
        return cls(CallType.REDOUBLE)

    @classmethod
    def bid(cls, level: int, strain: Strain) -> Call:
        return cls(CallType.BID, Bid(level, strain))


SEATS = ["N", "E", "S", "W"]
PARTNERSHIPS = {"N": "NS", "S": "NS", "E": "EW", "W": "EW"}
PARTNERS = {"N": "S", "S": "N", "E": "W", "W": "E"}


class Auction:
    def __init__(self, dealer: str) -> None:
        self.dealer = dealer
        self.calls: List[Tuple[str, Call]] = []
        self._current_seat_idx = SEATS.index(dealer)

    @property
    def current_seat(self) -> str:
        return SEATS[self._current_seat_idx % 4]

    @property
    def current_contract(self) -> Optional[Bid]:
        for _, call in reversed(self.calls):
            if call.call_type == CallType.BID:
                return call.bid
        return None

    @property
    def doubled(self) -> bool:
        for _, call in reversed(self.calls):
            if call.call_type == CallType.BID:
                return False
            if call.call_type == CallType.DOUBLE:
                return True
            if call.call_type == CallType.REDOUBLE:
                return False
        return False

    @property
    def redoubled(self) -> bool:
        for _, call in reversed(self.calls):
            if call.call_type == CallType.BID:
                return False
            if call.call_type == CallType.REDOUBLE:
                return True
            if call.call_type == CallType.DOUBLE:
                return False
        return False

    def declarer(self) -> Optional[str]:
        contract = self.current_contract
        if contract is None:
            return None
        winning_partnership = None
        for seat, call in self.calls:
            if call.call_type == CallType.BID and call.bid == contract:
                winning_partnership = PARTNERSHIPS[seat]
                break
        if winning_partnership is None:
            return None
        for seat, call in self.calls:
            if (
                call.call_type == CallType.BID
                and call.bid is not None
                and call.bid.strain == contract.strain
                and PARTNERSHIPS[seat] == winning_partnership
            ):
                return seat
        return None

    def is_finished(self) -> bool:
        if len(self.calls) < 4:
            return False
        last_four = [c.call_type for _, c in self.calls[-4:]]
        if all(t == CallType.PASS for t in last_four):
            return True
        if len(self.calls) >= 3:
            last_three = [c.call_type for _, c in self.calls[-3:]]
            if (
                all(t == CallType.PASS for t in last_three)
                and self.current_contract is not None
            ):
                return True
        return False

    def can_double(self) -> bool:
        contract = self.current_contract
        if contract is None:
            return False
        if self.doubled or self.redoubled:
            return False
        for seat, call in reversed(self.calls):
            if call.call_type == CallType.BID:
                return PARTNERSHIPS[seat] != PARTNERSHIPS[self.current_seat]
        return False

    def can_redouble(self) -> bool:
        if not self.doubled or self.redoubled:
            return False
        for seat, call in reversed(self.calls):
            if call.call_type == CallType.DOUBLE:
                return PARTNERSHIPS[seat] != PARTNERSHIPS[self.current_seat]
        return False

    def legal_bids(self) -> List[Bid]:
        contract = self.current_contract
        result = []
        for level in range(1, 8):
            for strain in Strain:
                b = Bid(level, strain)
                if contract is None or b > contract:
                    result.append(b)
        return result

    def make_call(self, call: Call) -> None:
        self.calls.append((self.current_seat, call))
        self._current_seat_idx += 1

    def passed_out(self) -> bool:
        return (
            len(self.calls) == 4
            and all(c.call_type == CallType.PASS for _, c in self.calls)
        )


# ---------------------------------------------------------------------------
# AI bidding
# ---------------------------------------------------------------------------

def _hcp(hand: List[Card]) -> int:
    return sum(c.hcp() for c in hand)


def _length_points(hand: List[Card]) -> int:
    by_suit = {s: 0 for s in Suit}
    for c in hand:
        by_suit[c.suit] += 1
    return sum(max(0, cnt - 4) for cnt in by_suit.values())


def _suit_counts(hand: List[Card]) -> dict:
    counts = {s: 0 for s in Suit}
    for c in hand:
        counts[c.suit] += 1
    return counts


def _is_balanced(hand: List[Card]) -> bool:
    counts = sorted(_suit_counts(hand).values())
    return counts in ([3, 3, 3, 4], [2, 3, 4, 4], [2, 3, 3, 5])


def _longest_suit(hand: List[Card]) -> Suit:
    counts = _suit_counts(hand)
    return max(counts, key=lambda s: (counts[s], int(s)))


def _suit_quality(hand: List[Card], suit: Suit) -> int:
    return sum(c.hcp() for c in hand if c.suit == suit)


def simple_ai_bid(hand: List[Card], auction: Auction) -> Call:
    hcp = _hcp(hand)
    tp = hcp + _length_points(hand)
    counts = _suit_counts(hand)
    balanced = _is_balanced(hand)
    legal = auction.legal_bids()
    contract = auction.current_contract
    partner = PARTNERS[auction.current_seat]
    my_side = PARTNERSHIPS[auction.current_seat]

    # Determine if our side opened and what opener bid
    opener_bid: Optional[Bid] = None
    my_bids = [call for seat, call in auction.calls
               if PARTNERSHIPS[seat] == my_side and call.call_type == CallType.BID]
    opp_bids = [call for seat, call in auction.calls
                if PARTNERSHIPS[seat] != my_side and call.call_type == CallType.BID]

    # Simple opener logic: first to speak for our side
    is_first_bid = len(my_bids) == 0

    if is_first_bid:
        # Opening bids
        if contract is None or all(
            PARTNERSHIPS[s] != my_side for s, c in auction.calls if c.call_type == CallType.BID
        ):
            # Opening seat — no interference from our side yet
            if tp >= 15 and tp <= 17 and balanced:
                b = Bid(1, Strain.NOTRUMP)
                if b in legal:
                    return Call.bid(1, Strain.NOTRUMP)
            if tp >= 13:
                best = _longest_suit(hand)
                strain = {
                    Suit.CLUBS: Strain.CLUBS,
                    Suit.DIAMONDS: Strain.DIAMONDS,
                    Suit.HEARTS: Strain.HEARTS,
                    Suit.SPADES: Strain.SPADES,
                }[best]
                b = Bid(1, strain)
                if b in legal:
                    return Call.bid(1, strain)
        # Pass weak hands
        return Call.pass_call()

    # Response / rebid logic
    if contract is not None:
        strain = contract.strain
        level = contract.level

        # Support partner's major with 3+ cards
        if strain in (Strain.HEARTS, Strain.SPADES):
            suit = strain.as_suit()
            if suit and counts[suit] >= 3:
                if hcp >= 6 and level < 4:
                    b = Bid(level + 1, strain)
                    if b in legal:
                        return Call.bid(level + 1, strain)
                elif hcp >= 13 and level < 4:
                    b = Bid(4, strain)
                    if b in legal:
                        return Call.bid(4, strain)

        # Bid NT with stopper-ish hand
        if hcp >= 8 and balanced and level == 1:
            b = Bid(2, Strain.NOTRUMP)
            if b in legal:
                return Call.bid(2, Strain.NOTRUMP)

    return Call.pass_call()
