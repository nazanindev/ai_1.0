from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .cards import Deck, Hand


@dataclass
class RoundResult:
    outcome: str          # 'blackjack' | 'win' | 'push' | 'lose' | 'bust'
    payout: int           # net change to bankroll (positive = gain, negative = loss)
    player_value: int
    dealer_value: int
    player_hand: Hand
    dealer_hand: Hand


class Game:
    def __init__(self, bankroll: int = 1000):
        self.bankroll = bankroll
        self._deck: Optional[Deck] = None

    def _ensure_deck(self) -> None:
        if self._deck is None:
            self._deck = Deck()

    def play_round(self, bet: int) -> RoundResult:
        if bet <= 0 or bet > self.bankroll:
            raise ValueError(f"Bet must be between 1 and {self.bankroll}")

        if self._deck is None or len(self._deck) < 52:
            self._deck = Deck()
        deck = self._deck

        player = Hand()
        dealer = Hand()

        player.add(deck.draw())
        dealer.add(deck.draw())
        player.add(deck.draw())
        dealer.add(deck.draw())

        return RoundResult(
            outcome='deal',
            payout=0,
            player_value=player.value(),
            dealer_value=dealer.value(),
            player_hand=player,
            dealer_hand=dealer,
        )

    def hit(self, hand: Hand) -> None:
        self._ensure_deck()
        hand.add(self._deck.draw())

    def dealer_play(self, dealer: Hand) -> None:
        self._ensure_deck()
        while dealer.value() < 17:
            dealer.add(self._deck.draw())

    def settle(self, bet: int, player: Hand, dealer: Hand, doubled: bool = False) -> RoundResult:
        actual_bet = bet * 2 if doubled else bet
        p_val = player.value()
        d_val = dealer.value()

        if player.is_bust():
            outcome, payout = 'bust', -actual_bet
        elif player.is_blackjack() and not dealer.is_blackjack():
            payout = int(actual_bet * 1.5)
            outcome = 'blackjack'
        elif dealer.is_bust():
            outcome, payout = 'win', actual_bet
        elif p_val > d_val:
            outcome, payout = 'win', actual_bet
        elif p_val == d_val:
            outcome, payout = 'push', 0
        else:
            outcome, payout = 'lose', -actual_bet

        self.bankroll += payout
        return RoundResult(
            outcome=outcome,
            payout=payout,
            player_value=p_val,
            dealer_value=d_val,
            player_hand=player,
            dealer_hand=dealer,
        )
