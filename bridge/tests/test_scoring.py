import pytest
from bridge.bidding import Bid, Strain
from bridge.scoring import score_contract


def test_3nt_made_exactly_nonvul():
    # 3NT exactly (9 tricks), not vulnerable, undoubled
    score = score_contract(Bid(3, Strain.NOTRUMP), tricks_made=9, doubled=False, redoubled=False, vulnerable=False)
    assert score == 400  # 40+30+30 = 100 trick score, 300 game bonus


def test_3nt_made_exactly_vulnerable():
    score = score_contract(Bid(3, Strain.NOTRUMP), tricks_made=9, doubled=False, redoubled=False, vulnerable=True)
    assert score == 600  # 100 trick score + 500 vul game bonus


def test_4spades_made_with_one_overtrick():
    # 4♠ = 120 trick score → game; one overtrick = 30 more
    score = score_contract(Bid(4, Strain.SPADES), tricks_made=11, doubled=False, redoubled=False, vulnerable=False)
    assert score == 450  # 120 + 300 game + 30 OT


def test_4spades_vulnerable_overtrick():
    score = score_contract(Bid(4, Strain.SPADES), tricks_made=11, doubled=False, redoubled=False, vulnerable=True)
    assert score == 650  # 120 + 500 vul game + 30 OT


def test_doubled_undertricks_nonvul():
    # 2 undertricks, doubled, not vulnerable: 100 + 200 = 300
    score = score_contract(Bid(3, Strain.NOTRUMP), tricks_made=7, doubled=True, redoubled=False, vulnerable=False)
    assert score == -300


def test_doubled_undertrick_one_nonvul():
    score = score_contract(Bid(2, Strain.SPADES), tricks_made=7, doubled=True, redoubled=False, vulnerable=False)
    assert score == -100


def test_small_slam_bonus_nonvul():
    # 6♠ made = 180 trick score (major 30×6) + 300 game + 500 small slam = 980
    score = score_contract(Bid(6, Strain.SPADES), tricks_made=12, doubled=False, redoubled=False, vulnerable=False)
    assert score == 980


def test_small_slam_bonus_vul():
    # 6♠ vul = 180 + 500 game + 750 slam = 1430
    score = score_contract(Bid(6, Strain.SPADES), tricks_made=12, doubled=False, redoubled=False, vulnerable=True)
    assert score == 1430


def test_grand_slam_bonus_nonvul():
    # 7NT = 220 trick score (40+30*6) + 300 game + 1000 grand = 1520
    score = score_contract(Bid(7, Strain.NOTRUMP), tricks_made=13, doubled=False, redoubled=False, vulnerable=False)
    assert score == 1520


def test_grand_slam_bonus_vul():
    # 7NT vul = 220 + 500 game + 1500 grand = 2220
    score = score_contract(Bid(7, Strain.NOTRUMP), tricks_made=13, doubled=False, redoubled=False, vulnerable=True)
    assert score == 2220


def test_part_score_bonus():
    # 1♠ made exactly = 30 + 50 part score = 80
    score = score_contract(Bid(1, Strain.SPADES), tricks_made=7, doubled=False, redoubled=False, vulnerable=False)
    assert score == 80


def test_undertricks_vulnerable():
    # 2 undertricks, not doubled, vulnerable: 2 × 100 = 200
    score = score_contract(Bid(3, Strain.NOTRUMP), tricks_made=7, doubled=False, redoubled=False, vulnerable=True)
    assert score == -200
