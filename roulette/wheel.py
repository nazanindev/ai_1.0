from __future__ import annotations
import random
from dataclasses import dataclass

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}


def _color(number: int) -> str:
    if number == 0:
        return "green"
    if number in RED_NUMBERS:
        return "red"
    return "black"


@dataclass(frozen=True)
class Pocket:
    number: int
    color: str

    def __str__(self) -> str:
        return f"{self.number} ({self.color})"


POCKETS: list[Pocket] = [Pocket(n, _color(n)) for n in range(37)]


class Wheel:
    def spin(self) -> Pocket:
        return random.choice(POCKETS)
