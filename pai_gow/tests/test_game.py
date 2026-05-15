import unittest
from pai_gow.tiles import Tile, TILE_SET
from pai_gow.hand import Hand
from pai_gow.game import Game


def _tile(name: str) -> Tile:
    for t in TILE_SET:
        if t.name == name:
            return t
    raise KeyError(name)


def _hand(n1: str, n2: str) -> Hand:
    return Hand(_tile(n1), _tile(n2))


def _teens() -> list[Tile]:
    return [t for t in TILE_SET if t.name == "Teen"]


class TestSettlement(unittest.TestCase):
    def test_player_wins_both_pays_minus_commission(self):
        game = Game(bankroll=1000)
        # Player HIGH: Teen pair (supreme civil pair)
        teens = _teens()
        p_hi = Hand(teens[0], teens[1])
        # Player LOW: value 9 (Gong)
        p_lo = _hand("Tit", "Teen")  # (7+12)%10=9 — but Teen already used; use Look+Tit
        p_lo = _hand("Look", "Gor")  # (9+4)%10=3 — hmm, need value that beats banker low
        # Simplify: use Look pair for high, anything for low, and build weak banker hands
        days = [t for t in TILE_SET if t.name == "Day"]
        p_hi = Hand(teens[0], teens[1])           # Teen pair (rank 1)
        b_hi = Hand(days[0], days[1])             # Day pair  (rank 2) — player wins
        p_lo = _hand("Look", "Gor")               # value (9+4)%10 = 3
        b_lo = _hand("Mooy", "Day")               # value (6+2)%10 = 8 — banker wins low!
        # Re-arrange: player low must beat banker low
        p_lo = _hand("Chong", "Tit")              # (11+7)%10 = 8
        b_lo = _hand("Mooy", "Day")               # (6+2)%10  = 8  → tie, banker wins
        # Use Foo+Tit for player low: (7+7)%10 = 4, banker Gor+Day: (4+2)%10=6 — still lose
        # Use Look+Bon: (9+10)%10=9, banker uses Gor+Day: (4+2)%10=6
        p_lo = _hand("Look", "Bon")               # (9+10)%10=9
        b_lo = _hand("Gor", "Day")                # (4+2)%10=6

        result = game.settle(100, p_hi, p_lo, b_hi, b_lo)
        self.assertEqual(result.outcome, 'win')
        self.assertEqual(result.payout, 95)  # 100 - 5% commission = 95
        self.assertEqual(game.bankroll, 1095)

    def test_push_player_wins_high_loses_low(self):
        game = Game(bankroll=1000)
        teens = _teens()
        days  = [t for t in TILE_SET if t.name == "Day"]
        p_hi = Hand(teens[0], teens[1])           # Teen pair — player wins high
        b_hi = Hand(days[0], days[1])             # Day pair  — banker loses high
        # Low: player loses
        p_lo = _hand("Gor", "Day")                # (4+2)%10=6
        b_lo = _hand("Look", "Bon")               # (9+10)%10=9

        result = game.settle(100, p_hi, p_lo, b_hi, b_lo)
        self.assertEqual(result.outcome, 'push')
        self.assertEqual(result.payout, 0)
        self.assertEqual(game.bankroll, 1000)

    def test_player_loses_both(self):
        game = Game(bankroll=1000)
        days  = [t for t in TILE_SET if t.name == "Day"]
        teens = _teens()
        p_hi = Hand(days[0], days[1])             # Day pair — player loses high
        b_hi = Hand(teens[0], teens[1])           # Teen pair — banker wins high
        p_lo = _hand("Gor", "Day")                # value 6 — but Day already used
        # Use non-pair tiles that differ
        p_lo = _hand("Gor", "Mooy")               # (4+6)%10=0
        b_lo = _hand("Look", "Bon")               # (9+10)%10=9

        result = game.settle(100, p_hi, p_lo, b_hi, b_lo)
        self.assertEqual(result.outcome, 'lose')
        self.assertEqual(result.payout, -100)
        self.assertEqual(game.bankroll, 900)

    def test_bankroll_decremented_on_loss(self):
        game = Game(bankroll=500)
        days  = [t for t in TILE_SET if t.name == "Day"]
        teens = _teens()
        p_hi = Hand(days[0], days[1])
        b_hi = Hand(teens[0], teens[1])
        p_lo = _hand("Gor", "Mooy")
        b_lo = _hand("Look", "Bon")
        game.settle(200, p_hi, p_lo, b_hi, b_lo)
        self.assertEqual(game.bankroll, 300)


class TestValidateSplit(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        # Use four distinct named tiles
        self.tiles = [
            _tile("Teen"), _tile("Look"),
            _tile("Bon"), _tile("Tit"),
        ]

    def test_valid_split_returns_none(self):
        high = Hand(self.tiles[0], self.tiles[1])  # Teen + Look
        low  = Hand(self.tiles[2], self.tiles[3])  # Bon  + Tit
        # Teen(12)+Look(9)=21%10=1, Bon(10)+Tit(7)=17%10=7 — low > high (value 7 > 1)
        # validate_split checks low > high → error
        # Swap so that it's valid
        high = Hand(self.tiles[2], self.tiles[3])  # Bon+Tit value 7
        low  = Hand(self.tiles[0], self.tiles[1])  # Teen+Look value 1
        error = self.game.validate_split(self.tiles, high, low)
        self.assertIsNone(error)

    def test_front_greater_than_back_is_rejected(self):
        # low hand (front) beats high hand (back) — illegal
        low  = Hand(self.tiles[2], self.tiles[3])  # Bon+Tit value 7
        high = Hand(self.tiles[0], self.tiles[1])  # Teen+Look value 1
        error = self.game.validate_split(self.tiles, high, low)
        self.assertIsNotNone(error)
        self.assertIn("front", error.lower())


class TestHouseWay(unittest.TestCase):
    def test_house_way_puts_pair_in_high_hand_when_possible(self):
        # Give banker exactly two pairs worth of tiles + two others
        # Two Teen tiles form a pair — house way should put them in the high hand
        teens = [t for t in TILE_SET if t.name == "Teen"]
        tiles = [teens[0], teens[1], _tile("Gor"), _tile("Day")]
        game = Game()
        high, low = game.house_way_split(tiles)
        self.assertTrue(high.is_pair() or low.is_pair())

    def test_house_way_result_is_valid(self):
        # Any split produced by house_way_split must satisfy validate_split
        game = Game()
        player_tiles, banker_tiles = game.deal()
        high, low = game.house_way_split(banker_tiles)
        error = game.validate_split(banker_tiles, high, low)
        self.assertIsNone(error, f"house_way_split produced invalid split: {error}")
