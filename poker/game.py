from __future__ import annotations
import os
import time
from typing import Callable

from poker.cards import Deck, Card
from poker.player import Player
from poker.hand_eval import evaluate
from poker import ui


STREETS = ["Pre-Flop", "Flop", "Turn", "River"]


class GameState:
    def __init__(
        self,
        players: list[Player],
        community: list[Card],
        pot: int,
        dealer_idx: int,
        current_idx: int | None,
        street: str,
        message: str = "",
    ) -> None:
        self.players = players
        self.community = community
        self.pot = pot
        self.dealer_idx = dealer_idx
        self.current_idx = current_idx
        self.street = street
        self.message = message


class TexasHoldem:
    def __init__(
        self,
        players: list[Player],
        small_blind: int = 10,
        big_blind: int = 20,
        action_callback: Callable[[GameState], None] | None = None,
    ) -> None:
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self._action_cb = action_callback
        self.dealer_idx = 0
        self.hand_num = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def play_hand(self, get_action: Callable[[Player, GameState, list[str]], str]) -> None:
        """Play a single hand of Texas Hold'em."""
        self.hand_num += 1
        deck = Deck()
        deck.shuffle()
        community: list[Card] = []
        pot = 0

        active_players = [p for p in self.players if p.chips > 0]
        if len(active_players) < 2:
            return

        for p in active_players:
            p.reset_for_hand()

        # Deal hole cards
        for _ in range(2):
            for p in active_players:
                p.hole_cards.append(deck.deal())

        # Blinds
        sb_idx, bb_idx = self._blind_indices(active_players)
        pot += active_players[sb_idx].bet(self.small_blind)
        pot += active_players[bb_idx].bet(self.big_blind)
        current_bet = self.big_blind

        # Streets
        for street_name, num_community in [
            ("Pre-Flop", 0),
            ("Flop", 3),
            ("Turn", 1),
            ("River", 1),
        ]:
            # Deal community cards
            for _ in range(num_community):
                community.append(deck.deal())

            # Reset per-street bets
            for p in active_players:
                p.reset_for_street()
            if street_name == "Pre-Flop":
                # Blinds already placed; restore current_bet tracking
                active_players[sb_idx].current_bet = self.small_blind
                active_players[bb_idx].current_bet = self.big_blind

            current_bet = self.big_blind if street_name == "Pre-Flop" else 0
            pot, current_bet = self._betting_round(
                active_players,
                community,
                pot,
                current_bet,
                street_name,
                first_to_act=(bb_idx + 1) % len(active_players) if street_name == "Pre-Flop" else (self.dealer_idx + 1) % len(active_players),
                get_action=get_action,
            )

            still_in = [p for p in active_players if not p.folded]
            if len(still_in) == 1:
                still_in[0].chips += pot
                state = GameState(active_players, community, pot, self._dealer_abs_idx(active_players), None, street_name,
                                  f"{still_in[0].name} wins {pot} chips (everyone else folded)")
                self._display(state)
                time.sleep(2)
                self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
                return

        # Showdown
        self._showdown(active_players, community, pot)
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _dealer_abs_idx(self, active_players: list[Player]) -> int:
        """Index within active_players list closest to global dealer_idx."""
        active_names = [p.name for p in active_players]
        all_names = [p.name for p in self.players]
        dealer_name = all_names[self.dealer_idx % len(all_names)]
        if dealer_name in active_names:
            return active_names.index(dealer_name)
        return 0

    def _blind_indices(self, active_players: list[Player]) -> tuple[int, int]:
        d = self._dealer_abs_idx(active_players)
        n = len(active_players)
        if n == 2:
            return d, (d + 1) % n
        return (d + 1) % n, (d + 2) % n

    def _betting_round(
        self,
        players: list[Player],
        community: list[Card],
        pot: int,
        current_bet: int,
        street: str,
        first_to_act: int,
        get_action: Callable[[Player, GameState, list[str]], str],
    ) -> tuple[int, int]:
        n = len(players)
        acted: set[int] = set()
        idx = first_to_act % n

        while True:
            p = players[idx]
            if p.folded or p.all_in:
                idx = (idx + 1) % n
                # Check if everyone else has acted
                eligibles = [i for i in range(n) if not players[i].folded and not players[i].all_in]
                if all(i in acted for i in eligibles):
                    break
                continue

            to_call = current_bet - p.current_bet
            options: list[str] = []
            if to_call == 0:
                options.append("check")
            else:
                options.append(f"call {to_call}")
            if p.chips > to_call:
                options.append("raise")
            options.append("fold")

            d_idx = self._dealer_abs_idx(players)
            state = GameState(players, community, pot, d_idx, idx, street)
            action = get_action(p, state, options)
            action = action.strip().lower()

            if action == "fold":
                p.fold()
            elif action.startswith("call") or action == "check":
                paid = p.bet(to_call)
                pot += paid
            elif action.startswith("raise"):
                parts = action.split()
                try:
                    raise_to = int(parts[1]) if len(parts) > 1 else current_bet * 2
                except ValueError:
                    raise_to = current_bet * 2
                raise_amount = max(raise_to - p.current_bet, self.big_blind)
                paid = p.bet(raise_amount)
                pot += paid
                current_bet = p.current_bet
                acted = {idx}  # everyone must act again after a raise
            else:
                # Default: check/call
                paid = p.bet(to_call)
                pot += paid

            acted.add(idx)
            idx = (idx + 1) % n

            still_fighting = [i for i in range(n) if not players[i].folded]
            if len(still_fighting) <= 1:
                break

            eligibles = [i for i in range(n) if not players[i].folded and not players[i].all_in]
            if all(i in acted for i in eligibles) and all(
                players[i].current_bet == current_bet for i in eligibles
            ):
                break

        return pot, current_bet

    def _showdown(self, players: list[Player], community: list[Card], pot: int) -> None:
        still_in = [p for p in players if not p.folded]
        scores = []
        for p in still_in:
            score, name = evaluate(p.hole_cards + community)
            scores.append((score, p, name))
        scores.sort(key=lambda x: x[0], reverse=True)
        best_score = scores[0][0]
        winners = [item for item in scores if item[0] == best_score]

        share = pot // len(winners)
        remainder = pot % len(winners)
        for i, (_, w, _) in enumerate(winners):
            w.chips += share + (1 if i == 0 else 0) * remainder

        results: list[tuple[Player, str, bool]] = []
        for p in players:
            if p.folded:
                results.append((p, "folded", False))
            else:
                score, name = evaluate(p.hole_cards + community)
                won = score == best_score
                results.append((p, name, won))

        winner_names = ", ".join(w.name for _, w, _ in winners)
        print(ui.render_showdown(players, community, results, pot))
        print(f"\n  {ui.bold(ui.yellow(f'Winner: {winner_names} (+{share} chips)'))}\n")
        time.sleep(3)

    def _display(self, state: GameState) -> None:
        _clear()
        print(ui.render_table(
            state.players,
            state.community,
            state.pot,
            state.dealer_idx,
            state.current_idx,
            state.street,
            state.message,
        ))


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")
