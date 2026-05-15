# Texas Hold'em — CLI Poker

A fully-featured Texas Hold'em poker game that runs in your terminal with colorful card art and ANSI styling.

## Running the game

```bash
# From the repo root
python -m poker
```

No dependencies beyond the Python standard library.

## Gameplay

You will be prompted for:
- **Your name** (default: Hero)
- **Starting chips** (default: 1000)
- **Number of AI opponents** 1–3 (default: 2)

### Controls during your turn

| Input | Action |
|-------|--------|
| `1` / `f` | Fold |
| `2` / `c` | Check (free) or Call |
| `3` / `r` | Raise (you will be asked for amount) |
| `q` | Quit |

### Rules summary

1. Each player is dealt **2 hole cards** (face down).
2. **Blinds** are posted by the two players left of the dealer button.
3. **Pre-Flop**: Players act in order starting left of the big blind. Options: fold, call, raise.
4. **Flop**: 3 community cards revealed. Betting starts left of dealer.
5. **Turn**: 4th community card. Another betting round.
6. **River**: 5th community card. Final betting round.
7. **Showdown**: Remaining players reveal hands. Best 5-card hand wins the pot.

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
╔════════════════════════════════════════════════════════════════════════╗
║  FLOP   pot: 120 chips
║  ────────────────────────────────────────────────────────────────────
║  ┌─────┐  ┌─────┐  ┌─────┐
║  │A    │  │K    │  │7    │
║  │  ♠  │  │  ♥  │  │  ♦  │
║  │    A│  │    K│  │    7│
║  └─────┘  └─────┘  └─────┘
║  ────────────────────────────────────────────────────────────────────
║  Hero [D] ◄ YOU ← action  820 chips
║    ┌─────┐  ┌─────┐
║    │A    │  │K    │
║    │  ♦  │  │  ♣  │
║    │    A│  │    K│
║    └─────┘  └─────┘
║
║  Atlas  230 chips
║    ┌─────┐  ┌─────┐
║    │░░░░░│  │░░░░░│
║    │░░░░░│  │░░░░░│
║    │░░░░░│  │░░░░░│
║    └─────┘  └─────┘
║
╚════════════════════════════════════════════════════════════════════════╝
```

## File structure

```
poker/
  __init__.py      — package marker
  __main__.py      — entry point for python -m poker
  cards.py         — Card, Suit, Rank, Deck
  hand_eval.py     — best 5-from-7 hand evaluator
  player.py        — Player model
  ai.py            — heuristic AI opponents
  game.py          — TexasHoldem game engine
  ui.py            — ANSI rendering helpers
  cli.py           — interactive CLI
```
