import unittest
from collections import deque
from blackjack.cards import Card, Hand
from blackjack.game import Game


def _hand(*specs) -> Hand:
    """Build a Hand from (rank, suit) tuples."""
    h = Hand()
    for rank, suit in specs:
        h.add(Card(rank, suit))
    return h


def _stub_deck(cards: list[Card]):
    q = deque(cards)

    class StubDeck:
        def draw(self):
            return q.popleft()

        def __len__(self):
            return len(q)

    return StubDeck()


class TestSettlement(unittest.TestCase):
    def test_player_blackjack_pays_3_to_2(self):
        game = Game(bankroll=1000)
        player = _hand(('A', '♠'), ('K', '♥'))
        dealer = _hand(('6', '♦'), ('9', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'blackjack')
        self.assertEqual(result.payout, 150)
        self.assertEqual(game.bankroll, 1150)

    def test_dealer_blackjack_player_loses(self):
        game = Game(bankroll=1000)
        player = _hand(('9', '♠'), ('8', '♥'))
        dealer = _hand(('A', '♦'), ('K', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'lose')
        self.assertEqual(result.payout, -100)
        self.assertEqual(game.bankroll, 900)

    def test_push_returns_bet(self):
        game = Game(bankroll=1000)
        player = _hand(('K', '♠'), ('9', '♥'))
        dealer = _hand(('Q', '♦'), ('9', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'push')
        self.assertEqual(result.payout, 0)
        self.assertEqual(game.bankroll, 1000)

    def test_player_wins_higher_value(self):
        game = Game(bankroll=1000)
        player = _hand(('K', '♠'), ('9', '♥'))
        dealer = _hand(('7', '♦'), ('9', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'win')
        self.assertEqual(result.payout, 100)

    def test_bust_loses_bet(self):
        game = Game(bankroll=1000)
        player = _hand(('K', '♠'), ('Q', '♥'), ('5', '♠'))  # 25, bust
        dealer = _hand(('7', '♦'), ('9', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'bust')
        self.assertEqual(result.payout, -100)

    def test_double_doubles_bet(self):
        game = Game(bankroll=1000)
        player = _hand(('6', '♠'), ('5', '♥'), ('K', '♦'))  # 21
        dealer = _hand(('7', '♦'), ('9', '♣'))               # 16
        result = game.settle(100, player, dealer, doubled=True)
        self.assertEqual(result.outcome, 'win')
        self.assertEqual(result.payout, 200)
        self.assertEqual(game.bankroll, 1200)

    def test_dealer_bust_player_wins(self):
        game = Game(bankroll=1000)
        player = _hand(('K', '♠'), ('8', '♥'))               # 18
        dealer = _hand(('6', '♦'), ('Q', '♣'), ('9', '♠'))  # 25, bust
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'win')

    def test_both_blackjack_is_push(self):
        game = Game(bankroll=1000)
        player = _hand(('A', '♠'), ('K', '♥'))
        dealer = _hand(('A', '♦'), ('Q', '♣'))
        result = game.settle(100, player, dealer)
        self.assertEqual(result.outcome, 'push')


class TestDealerPlay(unittest.TestCase):
    def test_dealer_hits_below_17(self):
        dealer = _hand(('6', '♠'), ('9', '♥'))  # 15
        game = Game(bankroll=500)
        game._deck = _stub_deck([Card('2', '♦')])
        game.dealer_play(dealer)
        self.assertGreaterEqual(dealer.value(), 17)

    def test_dealer_stands_on_17(self):
        dealer = _hand(('9', '♠'), ('8', '♥'))  # 17
        game = Game(bankroll=500)
        game._deck = _stub_deck([])
        game.dealer_play(dealer)
        self.assertEqual(dealer.value(), 17)

    def test_dealer_stands_soft_17(self):
        # A + 6 = soft 17; dealer must stand
        dealer = _hand(('A', '♠'), ('6', '♥'))
        game = Game(bankroll=500)
        game._deck = _stub_deck([])
        game.dealer_play(dealer)
        self.assertEqual(len(dealer.cards), 2)


if __name__ == '__main__':
    unittest.main()
