import pytest
from roulette.wheel import Wheel, POCKETS, RED_NUMBERS, BLACK_NUMBERS


def test_pocket_count():
    assert len(POCKETS) == 37


def test_zero_is_green():
    zero = next(p for p in POCKETS if p.number == 0)
    assert zero.color == "green"


def test_red_count():
    reds = [p for p in POCKETS if p.color == "red"]
    assert len(reds) == 18


def test_black_count():
    blacks = [p for p in POCKETS if p.color == "black"]
    assert len(blacks) == 18


def test_red_numbers_correct():
    reds = {p.number for p in POCKETS if p.color == "red"}
    assert reds == RED_NUMBERS


def test_black_numbers_correct():
    blacks = {p.number for p in POCKETS if p.color == "black"}
    assert blacks == BLACK_NUMBERS


def test_spin_returns_valid_pocket():
    wheel = Wheel()
    pocket = wheel.spin()
    assert pocket in POCKETS
    assert 0 <= pocket.number <= 36
    assert pocket.color in ("red", "black", "green")


def test_spin_coverage():
    wheel = Wheel()
    seen = set()
    for _ in range(10_000):
        seen.add(wheel.spin().number)
    assert seen == set(range(37))
