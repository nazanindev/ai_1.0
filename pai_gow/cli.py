import sys
from .game import Game
from .hand import Hand
from .tutorial import show_tutorial, show_instructions

_SEP = "=" * 52


def _prompt(msg: str, default: str = "") -> str:
    try:
        return input(msg).strip()
    except EOFError:
        return default


def _prompt_bet(bankroll: int) -> int:
    while True:
        raw = _prompt(f"\n  Bankroll: ${bankroll}  Bet (or 'q' to quit): ").lower()
        if raw in ('q', 'quit', ''):
            return 0
        try:
            bet = int(raw)
            if 1 <= bet <= bankroll:
                return bet
            print(f"    Bet must be between 1 and {bankroll}.")
        except ValueError:
            print("    Enter a whole number.")


def _render_tiles(tiles: list, label: str = "Your tiles") -> None:
    print(f"\n  {label}:")
    for i, tile in enumerate(tiles, 1):
        civil = f"  (civil rank {tile.civil_rank})" if tile.civil_rank else "  (military)"
        print(f"    [{i}] {tile}  {tile.name:10s}  {tile.chinese}  "
              f"{tile.total} pips{civil}")


def _prompt_split(tiles: list) -> tuple[Hand, Hand]:
    """
    Ask the player which two tiles form their HIGH hand.
    Returns (high_hand, low_hand).
    """
    while True:
        raw = _prompt(
            "\n  Pick your HIGH hand — enter 2 tile numbers (e.g. '1 3'), "
            "or '?' for help: "
        )
        if raw in ('q', 'quit'):
            print("\n  Cashing out...")
            sys.exit(0)
        if raw == '?':
            show_instructions()
            _render_tiles(tiles)
            continue
        parts = raw.split()
        if len(parts) != 2:
            print("    Enter exactly two tile numbers.")
            continue
        try:
            a, b = int(parts[0]), int(parts[1])
        except ValueError:
            print("    Enter two numbers (e.g. '1 3').")
            continue
        if not (1 <= a <= 4 and 1 <= b <= 4):
            print("    Tile numbers must be between 1 and 4.")
            continue
        if a == b:
            print("    Pick two different tiles.")
            continue
        hi_tiles = [tiles[a - 1], tiles[b - 1]]
        lo_tiles = [tiles[i] for i in range(4) if i + 1 not in (a, b)]
        return Hand(hi_tiles[0], hi_tiles[1]), Hand(lo_tiles[0], lo_tiles[1])


def _render_result(result) -> None:
    print("\n" + _SEP)
    print(f"  YOUR   HIGH: {result.player_high}")
    print(f"  YOUR   LOW:  {result.player_low}")
    print()
    print(f"  BANKER HIGH: {result.banker_high}")
    print(f"  BANKER LOW:  {result.banker_low}")
    print(_SEP)

    hi_win = result.player_high > result.banker_high
    lo_win = result.player_low  > result.banker_low
    hi_label = "WIN" if hi_win else ("TIE (banker wins)" if result.player_high == result.banker_high else "LOSE")
    lo_label = "WIN" if lo_win else ("TIE (banker wins)" if result.player_low  == result.banker_low  else "LOSE")
    print(f"  High hand: {hi_label}")
    print(f"  Low  hand: {lo_label}")

    msgs = {
        'win':  f"  You win ${result.payout} (after 5% commission)!",
        'push': "  Push — both hands returned.",
        'lose': f"  Banker wins. You lose ${abs(result.payout)}.",
    }
    print()
    print(msgs[result.outcome])


def _startup_menu() -> bool:
    """Returns True if the player chose to play."""
    while True:
        print()
        print("  [t] Tutorial       [i] Instructions")
        print("  [p] Play           [q] Quit")
        raw = _prompt("\n  Choice: ").lower()
        if raw in ('t', 'tutorial'):
            show_tutorial()
        elif raw in ('i', 'instructions', 'help'):
            show_instructions()
        elif raw in ('p', 'play', ''):
            return True
        elif raw in ('q', 'quit'):
            return False
        else:
            print("  Please enter t, i, p, or q.")


def main() -> None:
    print(_SEP)
    print("        PAI GOW TILES")
    print("  The ancient Chinese domino game")
    print("  Beat the banker's HIGH and LOW hands")
    print("  to win.  5% commission on wins.")
    print(_SEP)

    if not _startup_menu():
        print("\n  Goodbye!")
        sys.exit(0)

    try:
        raw = _prompt("\n  Starting bankroll [$1000]: ")
        starting = int(raw) if raw else 1000
    except ValueError:
        starting = 1000
    game = Game(bankroll=max(1, starting))

    while game.bankroll > 0:
        bet = _prompt_bet(game.bankroll)
        if bet == 0:
            print(f"\n  Cashing out with ${game.bankroll}. Thanks for playing!")
            sys.exit(0)

        player_tiles, banker_tiles = game.deal()

        _render_tiles(player_tiles)

        player_high, player_low = _prompt_split(player_tiles)

        error = game.validate_split(player_tiles, player_high, player_low)
        if error:
            print(f"\n    {error}")
            continue

        banker_high, banker_low = game.house_way_split(banker_tiles)

        result = game.settle(bet, player_high, player_low, banker_high, banker_low)
        _render_result(result)
        print(f"\n  Bankroll: ${game.bankroll}")

    print("\n  Out of chips. Game over!")
