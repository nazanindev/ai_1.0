from __future__ import annotations
import os
import random
import sys

from poker import ui
from poker.player import Player
from poker.game import TexasHoldem, GameState
from poker.ai import decide_action

_AI_NAMES = ["Atlas", "Blaze", "Colt", "Dex", "Echo", "Fox", "Ghost", "Haze"]


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _prompt(msg: str, default: str = "") -> str:
    try:
        val = input(msg).strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        return default


def _get_human_action(
    player: Player,
    state: GameState,
    options: list[str],
) -> str:
    _clear()
    print(ui.render_table(
        state.players,
        state.community,
        state.pot,
        state.dealer_idx,
        state.current_idx,
        state.street,
    ))

    print(f"\n  {ui.bold(ui.cyan('Your turn:'))}  {ui.dim(str(player.chips) + ' chips')}")
    print(f"  {ui.dim('Options:')} ", end="")
    labeled: list[str] = []
    for i, opt in enumerate(options, 1):
        labeled.append(f"[{i}] {opt}")
    print("  ".join(labeled))

    while True:
        raw = _prompt("  > ").strip().lower()

        # Numeric shortcut
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                chosen = options[idx]
                # Handle raise with amount
                if chosen == "raise":
                    amt = _prompt(f"  Raise amount (chips you have: {player.chips}): ").strip()
                    try:
                        int(amt)
                        return f"raise {amt}"
                    except ValueError:
                        print("  Invalid amount, defaulting to min raise.")
                        return "raise"
                return chosen

        # Text shortcut
        if raw in ("f", "fold"):
            if "fold" in options:
                return "fold"
        elif raw in ("c", "check") and "check" in options:
            return "check"
        elif raw.startswith("c") and any(o.startswith("call") for o in options):
            opt = next(o for o in options if o.startswith("call"))
            return opt
        elif raw.startswith("r") and "raise" in options:
            amt = _prompt(f"  Raise amount (chips you have: {player.chips}): ").strip()
            try:
                int(amt)
                return f"raise {amt}"
            except ValueError:
                return "raise"
        elif raw in ("q", "quit", "exit"):
            print(f"\n  {ui.yellow('Thanks for playing! Goodbye.')}\n")
            sys.exit(0)

        print(f"  {ui.dim('Enter a number or: f=fold, c=check/call, r=raise, q=quit')}")


def _get_ai_action(
    player: Player,
    state: GameState,
    options: list[str],
    aggressiveness: float,
) -> str:
    import time
    time.sleep(random.uniform(0.4, 1.0))  # simulate thinking
    action = decide_action(player, state, options, aggressiveness)
    return action


def _announce_action(player: Player, action: str) -> None:
    """Print a one-line announcement of what the bot did."""
    if action.startswith("raise"):
        parts = action.split()
        amt = parts[1] if len(parts) > 1 else "?"
        msg = ui.bold(ui.red(f"raises {amt}"))
    elif action.startswith("call"):
        parts = action.split()
        amt = parts[1] if len(parts) > 1 else "?"
        msg = ui.green(f"calls {amt}")
    elif action == "check":
        msg = ui.dim("checks")
    elif action == "fold":
        msg = ui.dim("folds")
    else:
        msg = ui.dim(action)
    print(f"  {ui.bold(player.name)}: {msg}")
    import time
    time.sleep(0.4)


def main() -> None:
    _clear()
    print(ui.BANNER)

    name = _prompt("  Enter your name [Hero]: ", "Hero")
    chips_str = _prompt("  Starting chips [1000]: ", "1000")
    try:
        starting_chips = int(chips_str)
    except ValueError:
        starting_chips = 1000

    num_bots_str = _prompt("  Number of AI opponents (1-3) [2]: ", "2")
    try:
        num_bots = max(1, min(3, int(num_bots_str)))
    except ValueError:
        num_bots = 2

    human = Player(name, starting_chips, is_human=True)
    bot_names = random.sample(_AI_NAMES, num_bots)
    bots = [
        Player(bname, starting_chips, is_human=False)
        for bname in bot_names
    ]
    # Assign random aggressiveness per bot
    aggressiveness_map = {b.name: round(random.uniform(0.2, 0.9), 2) for b in bots}

    all_players = [human] + bots

    small_blind = max(5, starting_chips // 200)
    big_blind = small_blind * 2

    _clear()
    print(ui.BANNER)
    print(f"  {ui.bold('Players:')} {', '.join(p.name for p in all_players)}")
    print(f"  {ui.bold('Blinds:')} {small_blind}/{big_blind}")
    print(f"  {ui.dim('Press Enter to start...')}")
    _prompt("")

    def get_action(player: Player, state: GameState, options: list[str]) -> str:
        if player.is_human:
            return _get_human_action(player, state, options)
        else:
            agg = aggressiveness_map.get(player.name, 0.5)
            action = _get_ai_action(player, state, options, agg)
            _clear()
            print(ui.render_table(
                state.players,
                state.community,
                state.pot,
                state.dealer_idx,
                state.current_idx,
                state.street,
            ))
            _announce_action(player, action)
            return action

    game = TexasHoldem(all_players, small_blind=small_blind, big_blind=big_blind)

    while True:
        active = [p for p in all_players if p.chips > 0]
        if len(active) < 2:
            winner = active[0] if active else None
            _clear()
            if winner:
                if winner.is_human:
                    print(f"\n  {ui.bold(ui.yellow('★ Congratulations! You win the game! ★'))}\n")
                else:
                    print(f"\n  {ui.bold(ui.red(f'Game over. {winner.name} wins everything.'))}\n")
            break

        game.play_hand(get_action)

        # Remove busted players
        busted = [p for p in all_players if p.chips == 0]
        for p in busted:
            print(f"  {ui.dim(p.name + ' is out of chips and leaves the table.')}")
            import time
            time.sleep(1)

        keep = _prompt(f"\n  {ui.bold('Play another hand?')} [y/n]: ", "y").lower()
        if keep not in ("y", "yes", ""):
            break

    print(f"\n  {ui.yellow('Thanks for playing Texas Hold''em! Goodbye.')}\n")


if __name__ == "__main__":
    main()
