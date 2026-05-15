import pytest
from roulette.wheel import Pocket
from roulette.bets import Bet, resolve


def pocket(n):
    from roulette.wheel import POCKETS
    return next(p for p in POCKETS if p.number == n)


# --- Straight (35:1) ---
def test_straight_win():
    b = Bet("straight", 7, 10)
    assert resolve(b, pocket(7)) == 350

def test_straight_loss():
    b = Bet("straight", 7, 10)
    assert resolve(b, pocket(8)) == -10

def test_straight_zero_win():
    b = Bet("straight", 0, 5)
    assert resolve(b, pocket(0)) == 175


# --- Color (1:1) ---
def test_color_red_win():
    b = Bet("color", "red", 20)
    assert resolve(b, pocket(1)) == 20   # 1 is red

def test_color_red_loss():
    b = Bet("color", "red", 20)
    assert resolve(b, pocket(2)) == -20  # 2 is black

def test_color_black_win():
    b = Bet("color", "black", 15)
    assert resolve(b, pocket(2)) == 15

def test_color_zero_loses():
    b = Bet("color", "red", 10)
    assert resolve(b, pocket(0)) == -10


# --- Parity (1:1) ---
def test_even_win():
    b = Bet("parity", "even", 10)
    assert resolve(b, pocket(4)) == 10

def test_even_loss():
    b = Bet("parity", "even", 10)
    assert resolve(b, pocket(3)) == -10

def test_odd_win():
    b = Bet("parity", "odd", 10)
    assert resolve(b, pocket(9)) == 10

def test_parity_zero_loses():
    b = Bet("parity", "even", 10)
    assert resolve(b, pocket(0)) == -10


# --- Half (1:1) ---
def test_low_win():
    b = Bet("half", "low", 10)
    assert resolve(b, pocket(18)) == 10

def test_low_loss():
    b = Bet("half", "low", 10)
    assert resolve(b, pocket(19)) == -10

def test_high_win():
    b = Bet("half", "high", 10)
    assert resolve(b, pocket(36)) == 10

def test_half_zero_loses():
    b = Bet("half", "low", 10)
    assert resolve(b, pocket(0)) == -10


# --- Dozen (2:1) ---
def test_dozen1_win():
    b = Bet("dozen", 1, 10)
    assert resolve(b, pocket(12)) == 20

def test_dozen2_win():
    b = Bet("dozen", 2, 10)
    assert resolve(b, pocket(13)) == 20

def test_dozen3_win():
    b = Bet("dozen", 3, 10)
    assert resolve(b, pocket(36)) == 20

def test_dozen_loss():
    b = Bet("dozen", 1, 10)
    assert resolve(b, pocket(13)) == -10

def test_dozen_zero_loses():
    b = Bet("dozen", 1, 10)
    assert resolve(b, pocket(0)) == -10


# --- Column (2:1) ---
def test_column1_win():
    # Column 1: numbers where (n-1) % 3 == 0 → 1,4,7,10,...
    b = Bet("column", 1, 10)
    assert resolve(b, pocket(1)) == 20

def test_column2_win():
    b = Bet("column", 2, 10)
    assert resolve(b, pocket(2)) == 20

def test_column3_win():
    b = Bet("column", 3, 10)
    assert resolve(b, pocket(3)) == 20

def test_column_loss():
    b = Bet("column", 1, 10)
    assert resolve(b, pocket(2)) == -10

def test_column_zero_loses():
    b = Bet("column", 1, 10)
    assert resolve(b, pocket(0)) == -10


# --- Unknown kind ---
def test_unknown_kind_raises():
    b = Bet("invalid", "x", 10)
    with pytest.raises(ValueError):
        resolve(b, pocket(5))
