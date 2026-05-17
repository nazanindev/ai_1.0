import pytest
from bridge.bidding import Bid, Strain
from bridge.cards import Card, Rank, Suit
from bridge.play import Trick, legal_plays, simple_ai_play


def _card(rank: Rank, suit: Suit) -> Card:
    return Card(rank, suit)


def test_must_follow_suit():
    hand = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.TWO, Suit.CLUBS),
    ]
    trick = Trick(trump=Suit.SPADES, lead_seat="N")
    trick.plays.append(("N", Card(Rank.FIVE, Suit.HEARTS)))  # led hearts

    legal = legal_plays(hand, trick)
    # Must play hearts if available
    assert all(c.suit == Suit.HEARTS for c in legal)
    assert len(legal) == 1


def test_can_play_any_when_void():
    hand = [
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.TWO, Suit.CLUBS),
    ]
    trick = Trick(trump=None, lead_seat="N")
    trick.plays.append(("N", Card(Rank.FIVE, Suit.HEARTS)))

    legal = legal_plays(hand, trick)
    assert len(legal) == 2  # no hearts in hand → can play anything


def test_trump_beats_non_trump():
    trick = Trick(trump=Suit.SPADES, lead_seat="N")
    trick.plays.append(("N", Card(Rank.ACE, Suit.HEARTS)))   # led ace of hearts
    trick.plays.append(("E", Card(Rank.TWO, Suit.HEARTS)))
    trick.plays.append(("S", Card(Rank.TWO, Suit.SPADES)))   # trumped with 2♠
    trick.plays.append(("W", Card(Rank.KING, Suit.HEARTS)))

    assert trick.winner() == "S"


def test_highest_lead_suit_wins_no_trump():
    trick = Trick(trump=None, lead_seat="N")
    trick.plays.append(("N", Card(Rank.FIVE, Suit.HEARTS)))
    trick.plays.append(("E", Card(Rank.ACE, Suit.HEARTS)))
    trick.plays.append(("S", Card(Rank.KING, Suit.HEARTS)))
    trick.plays.append(("W", Card(Rank.QUEEN, Suit.HEARTS)))

    assert trick.winner() == "E"


def test_cannot_overtrump_with_lower_trump():
    trick = Trick(trump=Suit.SPADES, lead_seat="N")
    trick.plays.append(("N", Card(Rank.ACE, Suit.HEARTS)))
    trick.plays.append(("E", Card(Rank.KING, Suit.SPADES)))   # trumped high
    trick.plays.append(("S", Card(Rank.TWO, Suit.SPADES)))    # lower trump
    trick.plays.append(("W", Card(Rank.THREE, Suit.HEARTS)))

    assert trick.winner() == "E"


def test_simple_ai_play_returns_legal_card():
    hand = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.TWO, Suit.CLUBS),
    ]
    contract = Bid(4, Strain.SPADES)
    trick = Trick(trump=Suit.SPADES, lead_seat="N")
    trick.plays.append(("N", Card(Rank.FIVE, Suit.HEARTS)))

    card = simple_ai_play(hand, trick, contract)
    legal = legal_plays(hand, trick)
    assert card in legal


def test_trick_complete_after_four_plays():
    trick = Trick(trump=None, lead_seat="N")
    cards = [
        ("N", Card(Rank.ACE, Suit.SPADES)),
        ("E", Card(Rank.KING, Suit.SPADES)),
        ("S", Card(Rank.QUEEN, Suit.SPADES)),
        ("W", Card(Rank.JACK, Suit.SPADES)),
    ]
    for seat, card in cards:
        trick.plays.append((seat, card))
    assert trick.is_complete
    assert trick.winner() == "N"  # ace wins


def test_lead_is_any_card():
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)]
    trick = Trick(trump=None, lead_seat="S")
    legal = legal_plays(hand, trick)
    assert set(legal) == set(hand)
