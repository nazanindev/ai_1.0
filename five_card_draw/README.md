# 5-Card Draw — CLI Poker

A fully-featured 5-Card Draw poker game that runs in your terminal with colorful card art and ANSI styling.

## Running the game

```bash
# From the repo root
python -m five_card_draw
```

No dependencies beyond the Python standard library.

## Gameplay

You will be prompted for:
- **Your name** (default: Hero)
- **Starting chips** (default: 1000)
- **Number of AI opponents** 1–3 (default: 2)

An **ante** is automatically collected from each player at the start of every hand.

### Controls during betting

| Input | Action |
|-------|--------|
| `1` / `f` | Fold |
| `2` / `c` | Check (free) or Call |
| `3` / `r` | Raise (you will be asked for amount) |
| `q` | Quit |

### Controls during the draw phase

You will see your 5 cards numbered `[1]` through `[5]`.

| Input | Action |
|-------|--------|
| `1,3,5` | Discard cards 1, 3, and 5 |
| `2` | Discard only card 2 |
| *(empty / `0`)* | Stand pat — keep all cards |

You may discard 0 to 5 cards.

### Rules summary

1. All players post an **ante**.
2. Each player is dealt **5 cards** face-down.
3. **First betting round**: fold, check/call, or raise.
4. **Draw phase**: each player discards 0–5 cards and receives that many replacements from the deck.
5. **Second betting round**: another round of fold, check/call, or raise.
6. **Showdown**: remaining players reveal hands. Best 5-card hand wins the pot.

### Hand rankings (best to worst)

| Rank | Hand |
|------|------|
| 1 | Royal Flush |
| 2 | Straight Flush |
| 3 | Four of a Kind |
| 4 | Full House |
| 5 | Flush |
| 6 | Straight (incl. wheel A-2-3-4-5) |
| 7 | Three of a Kind |
| 8 | Two Pair |
| 9 | One Pair |
| 10 | High Card |

## Example table view

```
╔════════════════════════════════════════════════════════════════════════════╗
║  First Bet   pot: 30 chips
║  ──────────────────────────────────────────────────────────────────────
║  Hero ◄ YOU ← action  985 chips
║    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
║    │A    │  │K    │  │7    │  │7    │  │2    │
║    │  ♠  │  │  ♥  │  │  ♦  │  │  ♣  │  │  ♠  │
║    │    A│  │    K│  │    7│  │    7│  │    2│
║    └─────┘  └─────┘  └─────┘  └─────┘  └─────┘
║
║  Atlas  985 chips
║    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
║    │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│
║    │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│
║    │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│  │░░░░░│
║    └─────┘  └─────┘  └─────┘  └─────┘  └─────┘
║
╚════════════════════════════════════════════════════════════════════════════╝
```

## File structure

```
five_card_draw/
  __init__.py      — package marker
  __main__.py      — entry point for python -m five_card_draw
  README.md        — this file
  cards.py         — Card, Suit, Rank, Deck
  hand_eval.py     — 5-card hand evaluator
  player.py        — Player model with discard support
  ai.py            — heuristic AI opponents (betting + discard decisions)
  ui.py            — ANSI rendering helpers and table layout
  game.py          — FiveCardDraw game engine
  cli.py           — interactive CLI
```
