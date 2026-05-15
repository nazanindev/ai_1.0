import sys
from .game import Game
from .cards import Hand


def _clear_line() -> None:
    print()


def _render_table(player: Hand, dealer: Hand, hide_hole: bool) -> None:
    print("\n" + "=" * 40)
    if hide_hole:
        hole = dealer.cards[1]
        visible = dealer.cards[0]
        print(f"Dealer: {visible}  ??  [?]")
    else:
        print(f"Dealer: {dealer}")
    print(f"You:    {player}")
    print("=" * 40)


def _prompt_bet(bankroll: int) -> int:
    while True:
        try:
            raw = input(f"\nBankroll: ${bankroll}  Place your bet (or 'q' to quit): ").strip().lower()
        except EOFError:
            return 0
        if raw in ('q', 'quit'):
            return 0
        try:
            bet = int(raw)
            if 1 <= bet <= bankroll:
                return bet
            print(f"  Bet must be between 1 and {bankroll}.")
        except ValueError:
            print("  Enter a whole number.")


def _prompt_action(can_double: bool) -> str:
    options = "[h]it  [s]tand" + ("  [d]ouble" if can_double else "")
    while True:
        try:
            raw = input(f"{options}: ").strip().lower()
        except EOFError:
            return 's'
        if raw in ('h', 'hit'):
            return 'h'
        if raw in ('s', 'stand'):
            return 's'
        if can_double and raw in ('d', 'double'):
            return 'd'
        print("  Please enter h, s" + (", or d" if can_double else "."))


def _show_result(result) -> None:
    msgs = {
        'blackjack': "BLACKJACK! You win ${payout}!",
        'win': "You win ${payout}!",
        'push': "Push — bet returned.",
        'lose': "Dealer wins. You lose ${loss}.",
        'bust': "Bust! You lose ${loss}.",
    }
    loss = abs(result.payout)
    msg = msgs[result.outcome].format(payout=result.payout, loss=loss)
    print(f"\n  {msg}")


def main() -> None:
    print("=" * 40)
    print("       BLACKJACK")
    print("  Dealer stands on soft 17")
    print("  Blackjack pays 3:2")
    print("=" * 40)

    try:
        starting = int(input("Starting bankroll [$1000]: ").strip() or "1000")
    except (ValueError, EOFError):
        starting = 1000

    game = Game(bankroll=max(1, starting))

    while game.bankroll > 0:
        bet = _prompt_bet(game.bankroll)
        if bet == 0:
            print(f"\nCashing out with ${game.bankroll}. Thanks for playing!")
            sys.exit(0)

        result = game.play_round(bet)
        player = result.player_hand
        dealer = result.dealer_hand

        _render_table(player, dealer, hide_hole=True)

        # Check for immediate blackjack
        if player.is_blackjack():
            game.dealer_play(dealer)
            _render_table(player, dealer, hide_hole=False)
            result = game.settle(bet, player, dealer)
            _show_result(result)
            if game.bankroll <= 0:
                break
            continue

        # Player turn
        doubled = False
        while True:
            can_double = len(player.cards) == 2 and game.bankroll >= bet
            action = _prompt_action(can_double)

            if action == 'h':
                game.hit(player)
                _render_table(player, dealer, hide_hole=True)
                if player.is_bust():
                    game.dealer_play(dealer)
                    _render_table(player, dealer, hide_hole=False)
                    result = game.settle(bet, player, dealer)
                    _show_result(result)
                    break
            elif action == 'd':
                game.hit(player)
                doubled = True
                _render_table(player, dealer, hide_hole=True)
                break
            else:  # stand
                break

        if not player.is_bust():
            game.dealer_play(dealer)
            _render_table(player, dealer, hide_hole=False)
            result = game.settle(bet, player, dealer, doubled=doubled)
            _show_result(result)

        print(f"  Bankroll: ${game.bankroll}")

    if game.bankroll <= 0:
        print("\nOut of money. Game over!")
