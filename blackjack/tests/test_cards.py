import unittest
from blackjack.cards import Card, Deck, Hand


class TestDeck(unittest.TestCase):
    def test_single_deck_size(self):
        d = Deck(num_decks=1)
        self.assertEqual(len(d), 52)

    def test_multi_deck_size(self):
        d = Deck(num_decks=6)
        self.assertEqual(len(d), 312)

    def test_unique_cards_in_single_deck(self):
        d = Deck(num_decks=1)
        cards = [d.draw() for _ in range(52)]
        identifiers = [(c.rank, c.suit) for c in cards]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_draw_reduces_count(self):
        d = Deck(num_decks=1)
        d.draw()
        self.assertEqual(len(d), 51)


class TestHandValue(unittest.TestCase):
    def _hand(self, *specs) -> Hand:
        h = Hand()
        for rank, suit in specs:
            h.add(Card(rank, suit))
        return h

    def test_simple_total(self):
        h = self._hand(('7', '♠'), ('8', '♥'))
        self.assertEqual(h.value(), 15)

    def test_face_cards_are_ten(self):
        h = self._hand(('K', '♠'), ('Q', '♥'))
        self.assertEqual(h.value(), 20)

    def test_single_ace_high(self):
        h = self._hand(('A', '♠'), ('6', '♥'))
        self.assertEqual(h.value(), 17)

    def test_single_ace_low(self):
        h = self._hand(('A', '♠'), ('6', '♥'), ('7', '♦'))
        self.assertEqual(h.value(), 14)

    def test_two_aces(self):
        h = self._hand(('A', '♠'), ('A', '♥'))
        self.assertEqual(h.value(), 12)

    def test_three_aces(self):
        h = self._hand(('A', '♠'), ('A', '♥'), ('A', '♦'))
        self.assertEqual(h.value(), 13)

    def test_bust_no_aces(self):
        h = self._hand(('K', '♠'), ('Q', '♥'), ('5', '♦'))
        self.assertTrue(h.is_bust())

    def test_ace_prevents_bust(self):
        h = self._hand(('A', '♠'), ('K', '♥'), ('9', '♦'))
        self.assertEqual(h.value(), 20)
        self.assertFalse(h.is_bust())


class TestBlackjack(unittest.TestCase):
    def test_natural_blackjack(self):
        h = Hand()
        h.add(Card('A', '♠'))
        h.add(Card('K', '♥'))
        self.assertTrue(h.is_blackjack())

    def test_21_not_blackjack_on_three_cards(self):
        h = Hand()
        h.add(Card('7', '♠'))
        h.add(Card('7', '♥'))
        h.add(Card('7', '♦'))
        self.assertFalse(h.is_blackjack())

    def test_20_is_not_blackjack(self):
        h = Hand()
        h.add(Card('K', '♠'))
        h.add(Card('Q', '♥'))
        self.assertFalse(h.is_blackjack())


if __name__ == '__main__':
    unittest.main()
