# Blackjack CLI

A command-line Blackjack game written in Python (standard library only).

## Run

```bash
python -m blackjack
```

## Rules

- **Decks:** 6-deck shoe, reshuffled when fewer than 52 cards remain.
- **Blackjack pays 3:2.**
- **Dealer stands on hard and soft 17.**
- **Double down** is available on any first two cards.
- No split, no surrender, no insurance.

## Actions

| Key | Action  |
|-----|---------|
| `h` | Hit     |
| `s` | Stand   |
| `d` | Double down (first two cards only) |
| `q` | Quit / cash out |

## Tests

```bash
python -m unittest discover blackjack/tests -v
```
