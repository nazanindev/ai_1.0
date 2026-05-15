from __future__ import annotations
from dataclasses import dataclass
from .wheel import Wheel, Pocket
from .bets import Bet, resolve


@dataclass
class SpinResult:
    pocket: Pocket
    bets: list[Bet]
    net: int   # total net change to balance


class Game:
    def __init__(self, balance: int = 1000):
        self.balance = balance
        self._wheel = Wheel()

    def place_bets(self, bets: list[Bet]) -> None:
        total = sum(b.amount for b in bets)
        if total <= 0:
            raise ValueError("Must place at least one bet with a positive amount.")
        if total > self.balance:
            raise ValueError(f"Total bets ${total} exceed balance ${self.balance}.")
        for b in bets:
            if b.amount <= 0:
                raise ValueError("Each bet amount must be positive.")

    def spin(self, bets: list[Bet]) -> SpinResult:
        self.place_bets(bets)
        pocket = self._wheel.spin()
        net = sum(resolve(b, pocket) for b in bets)
        self.balance += net
        return SpinResult(pocket=pocket, bets=bets, net=net)
