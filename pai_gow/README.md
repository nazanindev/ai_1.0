# Pai Gow Tiles CLI

A terminal-based Pai Gow Tiles game — the ancient Chinese domino gambling game you'll find in the quiet corner of every Asian casino.

## Run

```bash
python -m pai_gow
```

## Quick start

1. Choose a starting bankroll (default $1000).
2. Place your bet.
3. Four tiles are dealt to you. Select which two form your **HIGH (back)** hand by entering their numbers (e.g. `1 3`).
4. The remaining two become your **LOW (front)** hand.
5. The banker splits their tiles using the house way (automatic).
6. Your HIGH hand is compared to the banker's HIGH hand; your LOW hand to their LOW hand.
7. Win both → you win (minus 5% commission). Win one → push. Lose both → you lose.

## Tutorial & instructions

At startup, choose `[t]` for a multi-page interactive tutorial covering all rules, or `[i]` for a one-page quick reference. During play, enter `?` at any split prompt to re-display the quick reference.

## Rules summary

| Scenario | Outcome |
|---|---|
| Player wins HIGH and LOW | Win (95% of bet paid out) |
| Player wins one, loses one | Push (bet returned) |
| Player loses HIGH and LOW | Lose (full bet lost) |
| Exact tie on a hand | Banker wins ("copy" rule) |

* The high (back) hand **must** be stronger than or equal to the low (front) hand.
* A **pair** always beats a non-pair hand, regardless of pip count.
* Non-pair hand value = `(pip1 + pip2) mod 10`; maximum is **9** (called "Gong").

## Tile values & names

| Name | Pips | Total | Mod 10 | Civil rank |
|---|---|---|---|---|
| Teen | 6-6 | 12 | 2 | 1 (highest) |
| Day | 1-1 | 2 | 2 | 2 |
| Yan | 4-4 | 8 | 8 | 3 |
| Gor | 1-3 | 4 | 4 | 4 |
| Mooy | 1-5 | 6 | 6 | 5 |
| Chong | 5-6 | 11 | 1 | 6 |
| Bon | 4-6 | 10 | 0 | 7 |
| Foo | 1-6 | 7 | 7 | 8 |
| Ping | 2-6 | 8 | 8 | 9 |
| Tit | 2-5 | 7 | 7 | 10 |
| Look | 3-6 | 9 | 9 | 11 (lowest civil) |
| Gee Joon A | 2-4 | 6 | wild | military |
| Gee Joon B | 1-2 | 3 | wild | military |
| Mixed 9 | 1-8 / 4-5 | 9 | 9 | military |
| Mixed 8 | 3-5 / 2-6 | 8 | 8 | military |
| Mixed 7 | 1-6 / 2-5 | 7 | 7 | military |
| Mixed 5 | 1-4 / 2-3 | 5 | 5 | military |

**Gee Joon** tiles count as either 3 or 6 pips each — the game picks whichever value gives the stronger hand. When both Gee Joon tiles are in the same hand, they form the supreme pair.

## Pair rankings (highest → lowest)

1. **Gee Joon** — supreme pair (beats everything)
2. Teen, 3. Day, 4. Yan, 5. Gor, 6. Mooy, 7. Chong, 8. Bon
9. Foo, 10. Ping, 11. Tit, 12. Look
13. Mixed 9, 14. Mixed 8, 15. Mixed 7, 16. Mixed 5

## Example session

```
====================================================
        PAI GOW TILES
  The ancient Chinese domino game
  Beat the banker's HIGH and LOW hands
  to win.  5% commission on wins.
====================================================

  [t] Tutorial       [i] Instructions
  [p] Play           [q] Quit

  Choice: p

  Starting bankroll [$1000]: 500

  Bankroll: $500  Bet (or 'q' to quit): 50

  Your tiles:
    [1] [4:6]  Bon        板  10 pips  (civil rank 7)
    [2] [6:6]  Teen       天  12 pips  (civil rank 1)
    [3] [1:8]  Mix9-A     九   9 pips  (military)
    [4] [2:5]  Tit        七   7 pips  (civil rank 10)

  Pick your HIGH hand — enter 2 tile numbers (e.g. '1 3'): 2 3

====================================================
  YOUR   HIGH: [6:6]  [1:8]  = 5
  YOUR   LOW:  [4:6]  [2:5]  = 7
  BANKER HIGH: [...]  [...]  = 4
  BANKER LOW:  [...]  [...]  = 3
====================================================
  High hand: WIN
  Low  hand: WIN

  You win $47 (after 5% commission)!

  Bankroll: $547
```

## File structure

```
pai_gow/
  __init__.py      package marker
  __main__.py      entry point (python -m pai_gow)
  tiles.py         Tile dataclass, 32-tile TILE_SET, Deck, PAIR_RANKING
  hand.py          Hand class: value(), is_pair(), comparison operators
  game.py          Game class: deal(), house_way_split(), validate_split(), settle()
  tutorial.py      show_tutorial() and show_instructions()
  cli.py           main loop, prompts, ASCII rendering
  tests/
    test_hand.py   hand value, pair detection, comparison tests
    test_game.py   settlement, validate_split, house_way tests
```

## Tests

```bash
python -m unittest discover pai_gow/tests -v
```
