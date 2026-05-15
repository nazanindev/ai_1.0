from __future__ import annotations
import sys
import time
from .game import Game
from .bets import Bet

BET_MENU = """\
Bet types:
  1) Straight  — pick a number 0-36         pays 35:1
  2) Color     — red or black               pays 1:1
  3) Parity    — even or odd                pays 1:1
  4) Half      — low (1-18) or high (19-36) pays 1:1
  5) Dozen     — 1st/2nd/3rd dozen          pays 2:1
  6) Column    — 1st/2nd/3rd column         pays 2:1"""


def _spin_animation() -> None:
    frames = ["|", "/", "-", "\\"]
    for _ in range(12):
        print(f"\r  Spinning... {frames[_ % 4]}", end="", flush=True)
        time.sleep(0.07)
    print("\r" + " " * 20, end="\r")


def _prompt_int(prompt: str, lo: int, hi: int) -> int | None:
    while True:
        try:
            raw = input(prompt).strip().lower()
        except EOFError:
            return None
        if raw in ("q", "quit"):
            return None
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"  Enter a number between {lo} and {hi}.")
        except ValueError:
            print("  Enter a whole number (or q to quit).")


def _prompt_choice(prompt: str, choices: list[str]) -> str | None:
    while True:
        try:
            raw = input(prompt).strip().lower()
        except EOFError:
            return None
        if raw in ("q", "quit"):
            return None
        if raw in choices:
            return raw
        print(f"  Options: {', '.join(choices)}")


def _build_bet(balance: int) -> Bet | None:
    print(BET_MENU)
    bet_type = _prompt_int("\nChoose bet type (1-6, or q to quit): ", 1, 6)
    if bet_type is None:
        return None

    if bet_type == 1:
        val = _prompt_int("Pick a number (0-36): ", 0, 36)
        if val is None:
            return None
        kind, value = "straight", val
    elif bet_type == 2:
        v = _prompt_choice("Color [red/black]: ", ["red", "black"])
        if v is None:
            return None
        kind, value = "color", v
    elif bet_type == 3:
        v = _prompt_choice("Parity [even/odd]: ", ["even", "odd"])
        if v is None:
            return None
        kind, value = "parity", v
    elif bet_type == 4:
        v = _prompt_choice("Half [low/high]: ", ["low", "high"])
        if v is None:
            return None
        kind, value = "half", v
    elif bet_type == 5:
        v = _prompt_int("Dozen [1/2/3]: ", 1, 3)
        if v is None:
            return None
        kind, value = "dozen", v
    else:
        v = _prompt_int("Column [1/2/3]: ", 1, 3)
        if v is None:
            return None
        kind, value = "column", v

    amount = _prompt_int(f"Bet amount (1-{balance}): ", 1, balance)
    if amount is None:
        return None

    return Bet(kind=kind, value=value, amount=amount)


def main() -> None:
    print("=" * 44)
    print("           EUROPEAN ROULETTE")
    print("  Single-zero wheel  |  1 bet per spin")
    print("=" * 44)

    try:
        raw = input("Starting balance [$1000]: ").strip()
        starting = int(raw) if raw else 1000
    except (ValueError, EOFError):
        starting = 1000

    game = Game(balance=max(1, starting))

    while game.balance > 0:
        print(f"\n  Balance: ${game.balance}")
        bet = _build_bet(game.balance)
        if bet is None:
            print(f"\nCashing out with ${game.balance}. Thanks for playing!")
            sys.exit(0)

        _spin_animation()

        try:
            result = game.spin([bet])
        except ValueError as exc:
            print(f"  Error: {exc}")
            continue

        pocket = result.pocket
        color_tag = pocket.color.upper()
        print(f"  Ball landed on: {pocket.number}  [{color_tag}]")

        if result.net > 0:
            print(f"  You win ${result.net}!")
        elif result.net < 0:
            print(f"  You lose ${abs(result.net)}.")
        else:
            print("  Push — bet returned.")

        print(f"  Balance: ${game.balance}")

    print("\nOut of money. Game over!")
