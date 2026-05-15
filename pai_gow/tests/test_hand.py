import unittest
from pai_gow.tiles import Tile, TILE_SET
from pai_gow.hand import Hand

# Helper: look up a tile by name from the canonical TILE_SET
def _tile(name: str) -> Tile:
    for t in TILE_SET:
        if t.name == name:
            return t
    raise KeyError(name)


def _hand(n1: str, n2: str) -> Hand:
    return Hand(_tile(n1), _tile(n2))


class TestHandValue(unittest.TestCase):
    def test_value_mod_ten(self):
        # Bon(4+6=10) + Chong(5+6=11) = 21  →  1
        h = _hand("Bon", "Chong")
        self.assertFalse(h.is_pair())
        self.assertEqual(h.value(), 1)

    def test_gong_is_nine(self):
        # Look(3+6=9) + Day(1+1=2) = 11  →  1 — not 9, just confirming mod 10
        h_look_day = _hand("Look", "Day")
        self.assertEqual(h_look_day.value(), 1)
        # Yan(4+4=8) + Gor(1+3=4) = 12  →  2
        h_yan_gor = _hand("Yan", "Gor")
        self.assertEqual(h_yan_gor.value(), 2)
        # Tit(2+5=7) + Teen(6+6=12) = 19  →  9 (Gong)
        h_gong = _hand("Tit", "Teen")
        self.assertEqual(h_gong.value(), 9)

    def test_gee_joon_wild_chooses_best(self):
        # GeeJoon-A with Look(3+6=9):
        #   count GeeJoon-A as 6: (6+9)%10 = 5
        #   count GeeJoon-A as 3: (3+9)%10 = 2
        # Should pick 5
        h = Hand(_tile("GeeJoon-A"), _tile("Look"))
        self.assertEqual(h.value(), 5)

    def test_pair_detection(self):
        # Two Teen tiles form a civil pair
        teens = [t for t in TILE_SET if t.name == "Teen"]
        self.assertEqual(len(teens), 2)
        h = Hand(teens[0], teens[1])
        self.assertTrue(h.is_pair())
        self.assertEqual(h.pair_name(), "Teen")

    def test_gee_joon_pair(self):
        gj_a = _tile("GeeJoon-A")
        gj_b = _tile("GeeJoon-B")
        h = Hand(gj_a, gj_b)
        self.assertTrue(h.is_pair())
        self.assertEqual(h.pair_name(), "GeeJoon")

    def test_military_mixed_pair(self):
        h = Hand(_tile("Mix9-A"), _tile("Mix9-B"))
        self.assertTrue(h.is_pair())
        self.assertEqual(h.pair_name(), "Mix9")

    def test_different_pair_names_not_a_pair(self):
        h = Hand(_tile("Teen"), _tile("Day"))
        self.assertFalse(h.is_pair())


class TestHandComparison(unittest.TestCase):
    def test_pair_beats_non_pair(self):
        teens = [t for t in TILE_SET if t.name == "Teen"]
        pair_hand = Hand(teens[0], teens[1])
        non_pair = _hand("Look", "Tit")  # value 9 (gong)
        self.assertGreater(pair_hand, non_pair)
        self.assertLess(non_pair, pair_hand)

    def test_gee_joon_is_highest_pair(self):
        gj = Hand(_tile("GeeJoon-A"), _tile("GeeJoon-B"))
        teens = [t for t in TILE_SET if t.name == "Teen"]
        teen_pair = Hand(teens[0], teens[1])
        self.assertGreater(gj, teen_pair)

    def test_lower_civil_pair_beats_higher_numbered_pair(self):
        teens = [t for t in TILE_SET if t.name == "Teen"]
        days  = [t for t in TILE_SET if t.name == "Day"]
        teen_pair = Hand(teens[0], teens[1])
        day_pair  = Hand(days[0], days[1])
        # Teen is rank 1, Day is rank 2 → Teen is higher
        self.assertGreater(teen_pair, day_pair)

    def test_higher_value_beats_lower_value(self):
        h9 = _hand("Tit", "Teen")   # (7+12)%10 = 9
        h5 = _hand("Mooy", "Day")   # (6+2)%10  = 8  wait let me recalculate
        # Mooy pips: 1+5=6, Day pips: 1+1=2  → 8
        # h5 value should be 8, h9 value 9 → h9 > h5
        self.assertEqual(h9.value(), 9)
        self.assertEqual(h5.value(), 8)
        self.assertGreater(h9, h5)

    def test_tie_is_equal(self):
        # Two different non-pair hands with same value are "equal" (banker wins ties in settle)
        h_a = _hand("Bon", "Chong")   # (10+11)%10 = 1
        h_b = _hand("Foo", "Day")     # (7+2)%10   = 9  not same as above
        # Let's find two hands that have same value mod 10
        # Teen(12) + Yan(8) = 20 % 10 = 0
        # Bon(10)  + Day(2) = 12 % 10 = 2
        h_x = _hand("Teen", "Day")     # 14 % 10 = 4
        h_y = _hand("Gor", "Day")      # (4+2) % 10 = 6  not same
        # Let's just test equality directly:
        # Gor(1+3=4) + Chong(5+6=11) = 15 % 10 = 5
        # Mooy(1+5=6) + Foo(1+6=7) = 13 % 10 = 3  not same
        # Tit(2+5=7) + Gor(1+3=4) = 11 % 10 = 1
        # Chong(5+6=11) + Bon(4+6=10) = 21 % 10 = 1 — same!
        h_c = _hand("Tit", "Gor")
        h_d = _hand("Chong", "Bon")
        self.assertEqual(h_c.value(), 1)
        self.assertEqual(h_d.value(), 1)
        self.assertEqual(h_c, h_d)
        self.assertFalse(h_c > h_d)
        self.assertFalse(h_c < h_d)
