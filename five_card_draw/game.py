from __future__ import annotations
import os
import time
from typing import Callable

from five_card_draw.cards import Deck, Card
from five_card_draw.player import Player
from five_card_draw.hand_eval import evaluate
from five_card_draw import ui


class GameState:
    def __init__(
        self,
        players: list[Player],
        pot: int,
        dealer_idx: int,
        current_idx: int | None,
        phase: str,
        message: str = "",
    ) -> None:
        self.players = players
        self.pot = pot
        self.dealer_idx = dealer_idx
        self.current_idx = current_idx
        self.phase = phase
        self.message = message


class FiveCardDraw:
    def __init__(
        self,
        players: list[Player],
        ante: int = 5,
        action_callback: Callable[[GameState], None] | None = None,
    ) -> None:
        self.players = players
        self.ante = ante
        self._action_cb = action_callback
        self.dealer_idx = 0
        self.hand_num = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def play_hand(
        self,
        get_action: Callable[[Player, GameState, list[str]], str],
        get_discard: Callable[[Player, GameState], list[int]],
    ) -> None:
        """Play a single hand of 5-Card Draw."""
        self.hand_num += 1
        deck = Deck()
        deck.shuffle()
        pot = 0

        active_players = [p for p in self.players if p.chips > 0]
        if len(active_players) < 2:
            return

        for p in active_players:
            p.reset_for_hand()

        # (a) Collect ante
        for p in active_players:
            paid = p.bet(min(self.ante, p.chips))
            pot += paid

        # (b) Deal 5 cards to each player
        for _ in range(5):
            for p in active_players:
                p.hand.append(deck.deal())

        # Determine first to act (left of dealer)
        d_abs = self._dealer_abs_idx(active_players)
        first_to_act = (d_abs + 1) % len(active_players)

        # (c) First betting round
        phase = "First Bet"
        for p in active_players:
            p.reset_for_street()
        pot, _ = self._betting_round(
            active_players, pot, 0, phase, first_to_act, get_action
        )

        still_in = [p for p in active_players if not p.folded]
        if len(still_in) == 1:
            self._award_pot(still_in[0], pot, active_players, phase)
            self._advance_dealer()
            return

        # (d) Draw phase
        phase = "Draw"
        for idx, p in enumerate(active_players):
            if p.folded:
                continue
            state = GameState(active_players, pot, d_abs, idx, phase)
            discard_indices = get_discard(p, state)
            # Validate: only 0-based indices 0–4
            discard_indices = [i for i in discard_indices if 0 <= i <= 4]
            p.discard(discard_indices)
            for _ in range(len(discard_indices)):
                if len(deck) > 0:
                    p.hand.append(deck.deal())

        # (e) Second betting round
        phase = "Second Bet"
        for p in active_players:
            p.reset_for_street()
        pot, _ = self._betting_round(
            active_players, pot, 0, phase, first_to_act, get_action
        )

        still_in = [p for p in active_players if not p.folded]
        if len(still_in) == 1:
            self._award_pot(still_in[0], pot, active_players, phase)
            self._advance_dealer()
            return

        # (f) Showdown
        self._showdown(active_players, pot)
        self._advance_dealer()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _dealer_abs_idx(self, active_players: list[Player]) -> int:
        active_names = [p.name for p in active_players]
        all_names = [p.name for p in self.players]
        dealer_name = all_names[self.dealer_idx % len(all_names)]
        if dealer_name in active_names:
            return active_names.index(dealer_name)
        return 0

    def _advance_dealer(self) -> None:
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)

    def _betting_round(
        self,
        players: list[Player],
        pot: int,
        current_bet: int,
        phase: str,
        first_to_act: int,
        get_action: Callable[[Player, GameState, list[str]], str],
    ) -> tuple[int, int]:
        n = len(players)
        acted: set[int] = set()
        idx = first_to_act % n
        d_abs = self._dealer_abs_idx(players)

        while True:
            p = players[idx]
            if p.folded or p.all_in:
                idx = (idx + 1) % n
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

            state = GameState(players, pot, d_abs, idx, phase)
            action = get_action(p, state, options).strip().lower()

            if action == "fold":
                p.fold()
            elif action.startswith("call") or action == "check":
                paid = p.bet(to_call)
                pot += paid
            elif action.startswith("raise"):
                parts = action.split()
                try:
                    raise_to = int(parts[1]) if len(parts) > 1 else (current_bet + self.ante * 2)
                except ValueError:
                    raise_to = current_bet + self.ante * 2
                raise_amount = max(raise_to - p.current_bet, self.ante)
                paid = p.bet(raise_amount)
                pot += paid
                current_bet = p.current_bet
                acted = {idx}
            else:
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

    def _award_pot(
        self,
        winner: Player,
        pot: int,
        all_active: list[Player],
        phase: str,
    ) -> None:
        winner.chips += pot
        state = GameState(
            all_active, pot, self._dealer_abs_idx(all_active), None, phase,
            f"{winner.name} wins {pot} chips (everyone else folded)"
        )
        _clear()
        print(ui.render_table(state.players, state.pot, state.current_idx, state.phase, state.message))
        time.sleep(2)

    def _showdown(self, players: list[Player], pot: int) -> None:
        still_in = [p for p in players if not p.folded]
        scores = []
        for p in still_in:
            if len(p.hand) == 5:
                score, name = evaluate(p.hand)
            else:
                score, name = ((-1,), "Incomplete hand")
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
                if len(p.hand) == 5:
                    score, name = evaluate(p.hand)
                    won = score == best_score
                else:
                    name, won = "Incomplete hand", False
                results.append((p, name, won))

        winner_names = ", ".join(w.name for _, w, _ in winners)
        _clear()
        print(ui.render_showdown(players, results, pot))
        print(f"\n  {ui.bold(ui.yellow(f'Winner: {winner_names} (+{share} chips)'))}\n")
        time.sleep(3)


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")
