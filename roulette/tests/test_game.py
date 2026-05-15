import pytest
from unittest.mock import patch
from roulette.game import Game
from roulette.bets import Bet
from roulette.wheel import POCKETS


def _pocket(n):
    return next(p for p in POCKETS if p.number == n)


def test_initial_balance():
    game = Game(balance=500)
    assert game.balance == 500


def test_spin_win_updates_balance():
    game = Game(balance=100)
    bets = [Bet("color", "red", 10)]
    with patch.object(game._wheel, "spin", return_value=_pocket(1)):  # 1 is red
        result = game.spin(bets)
    assert result.net == 10
    assert game.balance == 110


def test_spin_loss_updates_balance():
    game = Game(balance=100)
    bets = [Bet("color", "black", 10)]
    with patch.object(game._wheel, "spin", return_value=_pocket(1)):  # 1 is red → loss
        result = game.spin(bets)
    assert result.net == -10
    assert game.balance == 90


def test_spin_straight_win():
    game = Game(balance=200)
    bets = [Bet("straight", 7, 5)]
    with patch.object(game._wheel, "spin", return_value=_pocket(7)):
        result = game.spin(bets)
    assert result.net == 175   # 35 * 5
    assert game.balance == 375


def test_bet_exceeds_balance_raises():
    game = Game(balance=50)
    with pytest.raises(ValueError, match="exceed balance"):
        game.spin([Bet("color", "red", 100)])


def test_zero_amount_raises():
    game = Game(balance=100)
    with pytest.raises(ValueError):
        game.spin([Bet("color", "red", 0)])


def test_negative_amount_raises():
    game = Game(balance=100)
    with pytest.raises(ValueError):
        game.spin([Bet("color", "red", -5)])


def test_no_bets_raises():
    game = Game(balance=100)
    with pytest.raises(ValueError):
        game.spin([])


def test_green_zero_loses_color_bet():
    game = Game(balance=100)
    bets = [Bet("color", "red", 10)]
    with patch.object(game._wheel, "spin", return_value=_pocket(0)):
        result = game.spin(bets)
    assert result.net == -10
    assert game.balance == 90
