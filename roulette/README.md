# Roulette

European single-zero roulette CLI game.

## How to play

```
python -m roulette
```

Choose your bet type, pick your value, enter your wager, and the wheel spins. Win or lose, keep playing until you cash out or go broke.

## Bet types and payouts

| Bet | Description | Payout |
|-----|-------------|--------|
| Straight | Exact number (0-36) | 35:1 |
| Color | Red or Black | 1:1 |
| Parity | Even or Odd | 1:1 |
| Half | Low (1-18) or High (19-36) | 1:1 |
| Dozen | 1st (1-12), 2nd (13-24), 3rd (25-36) | 2:1 |
| Column | 1st, 2nd, or 3rd column of the layout | 2:1 |

Zero (0) is green and loses all even-money and outside bets.

## Wheel

European layout with 37 pockets: 0 (green), 18 red, 18 black.

Red numbers: 1 3 5 7 9 12 14 16 18 19 21 23 25 27 30 32 34 36  
Black numbers: 2 4 6 8 10 11 13 15 17 20 22 24 26 28 29 31 33 35

## Running tests

```
python -m pytest roulette/tests/
```
