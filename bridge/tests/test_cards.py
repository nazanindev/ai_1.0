import pytest
from bridge.cards import Card, Deck, Rank, Suit


def test_deck_size():
    deck = Deck(seed=0)
    assert len(deck._cards) == 52


def test_deck_unique_cards():
    deck = Deck(seed=0)
    assert len(set((c.rank, c.suit) for c in deck._cards)) == 52


def test_deal_produces_four_hands_of_13():
    deck = Deck(seed=42)
    hands = deck.deal()
    assert set(hands.keys()) == {"N", "E", "S", "W"}
    for seat, hand in hands.items():
        assert len(hand) == 13, f"{seat} has {len(hand)} cards"


def test_deal_all_52_cards_distributed():
    deck = Deck(seed=7)
    hands = deck.deal()
    all_cards = [c for hand in hands.values() for c in hand]
    assert len(all_cards) == 52
    assert len(set((c.rank, c.suit) for c in all_cards)) == 52


def test_suit_rank_ordering():
    assert Suit.CLUBS < Suit.DIAMONDS < Suit.HEARTS < Suit.SPADES
    assert Rank.TWO < Rank.TEN < Rank.JACK < Rank.QUEEN < Rank.KING < Rank.ACE


def test_card_comparison():
    ace_spades = Card(Rank.ACE, Suit.SPADES)
    two_clubs = Card(Rank.TWO, Suit.CLUBS)
    assert two_clubs < ace_spades


def test_card_hcp():
    assert Card(Rank.ACE, Suit.SPADES).hcp() == 4
    assert Card(Rank.KING, Suit.HEARTS).hcp() == 3
    assert Card(Rank.QUEEN, Suit.DIAMONDS).hcp() == 2
    assert Card(Rank.JACK, Suit.CLUBS).hcp() == 1
    assert Card(Rank.TEN, Suit.SPADES).hcp() == 0


def test_suit_symbols():
    assert Suit.SPADES.symbol() == "♠"
    assert Suit.HEARTS.symbol() == "♥"
    assert Suit.DIAMONDS.symbol() == "♦"
    assert Suit.CLUBS.symbol() == "♣"
