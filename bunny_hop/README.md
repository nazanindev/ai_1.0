# Bunny Hop

A cute terminal game where you guide a bunny around a grid, gobbling up carrots while foxes close in.

## How to run

```bash
python -m bunny_hop
```

Requires Python 3.10+ and a terminal that supports curses (macOS Terminal, iTerm2, Linux terminal emulators). Windows users need a WSL shell.

## Premise

You are `B`, a bunny on a 20x10 grid. Carrots (`c`) are scattered around — eat them all to score points. But watch out for foxes (`F`) that hunt you down. Each level adds another fox and they get faster.

## Controls

| Key | Action |
|-----|--------|
| Arrow Up / Down / Left / Right | Move the bunny one cell |
| `Q` | Quit the game |
| `R` | Restart after game over |

## Scoring

| Event | Points |
|-------|--------|
| Eat a carrot | +10 |

## Levelling up

Every 5 carrots collected triggers a level-up:
- A new fox spawns on the grid.
- Foxes move faster (speed increases with each level, capping at maximum chase speed around level 4).
- The level-up message flashes briefly on screen.

## Lives

You start with **3 hearts**. Each fox collision costs one heart. After a hit you gain a brief invincibility window (bunny turns blue) so you can escape before the next hit counts. When all hearts are gone it's game over.

## Architecture

| File | Purpose |
|------|---------|
| `__main__.py` | Entry point — wraps `cli.main` with `curses.wrapper` |
| `cli.py` | Curses rendering loop, input handling, game-over screen |
| `game.py` | `BunnyHopGame` class: state, rules, tick logic |
| `entities.py` | `Bunny`, `Carrot`, `Fox` dataclasses with movement helpers |

### Game loop

1. `cli.py` sets a `TICK_MS = 150` ms timeout on `stdscr.getch()`.
2. On each wakeup (key press **or** timeout), `game.update(direction)` is called.
3. `update` moves the bunny (if a direction was pressed), moves foxes, checks collisions, awards points, and handles level-up.
4. The grid is redrawn after every tick.

### Fox AI

Each fox advances one cell per tick toward the bunny, moving along whichever axis has the greater distance first (Manhattan-distance greedy chase). At higher levels a random throttle is removed so foxes step every tick.
