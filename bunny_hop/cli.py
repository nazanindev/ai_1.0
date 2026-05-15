import curses
import sys
from .game import BunnyHopGame

# Tick interval in milliseconds — foxes move on every tick even without input
TICK_MS = 150

# Curses color pair IDs
COLOR_BUNNY   = 1
COLOR_CARROT  = 2
COLOR_FOX     = 3
COLOR_WALL    = 4
COLOR_HEADER  = 5
COLOR_FLASH   = 6
COLOR_INVINCIBLE = 7


def _init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_BUNNY,      curses.COLOR_WHITE,   -1)
    curses.init_pair(COLOR_CARROT,     curses.COLOR_YELLOW,  -1)
    curses.init_pair(COLOR_FOX,        curses.COLOR_RED,     -1)
    curses.init_pair(COLOR_WALL,       curses.COLOR_CYAN,    -1)
    curses.init_pair(COLOR_HEADER,     curses.COLOR_GREEN,   -1)
    curses.init_pair(COLOR_FLASH,      curses.COLOR_MAGENTA, -1)
    curses.init_pair(COLOR_INVINCIBLE, curses.COLOR_BLUE,    -1)


def _draw(stdscr: "curses.window", game: BunnyHopGame) -> None:
    stdscr.erase()
    w, h = game.width, game.height
    row_offset = 2  # rows reserved for header

    # Header
    lives_str  = "hearts " + "* " * game.bunny.lives
    score_str  = f"Score: {game.score}"
    level_str  = f"Level: {game.level}"
    header = f"  {score_str}   {level_str}   {lives_str}"
    stdscr.addstr(0, 0, header, curses.color_pair(COLOR_HEADER) | curses.A_BOLD)

    controls = "  Arrows: move   Q: quit"
    stdscr.addstr(1, 0, controls)

    if game.level_up_flash > 0:
        msg = f"  *** LEVEL {game.level}! ***"
        stdscr.addstr(1, 0, msg, curses.color_pair(COLOR_FLASH) | curses.A_BOLD)

    # Top wall
    wall_line = "#" * (w + 2)
    stdscr.addstr(row_offset, 0, wall_line, curses.color_pair(COLOR_WALL))

    # Grid rows
    carrot_cells = {(c.x, c.y) for c in game.carrots}
    fox_cells    = {(f.x, f.y) for f in game.foxes}

    for y in range(h):
        stdscr.addstr(row_offset + 1 + y, 0, "#", curses.color_pair(COLOR_WALL))
        for x in range(w):
            cell_row = row_offset + 1 + y
            cell_col = 1 + x
            if x == game.bunny.x and y == game.bunny.y:
                pair = COLOR_INVINCIBLE if game.bunny.is_invincible else COLOR_BUNNY
                stdscr.addstr(cell_row, cell_col, "B", curses.color_pair(pair) | curses.A_BOLD)
            elif (x, y) in fox_cells:
                stdscr.addstr(cell_row, cell_col, "F", curses.color_pair(COLOR_FOX) | curses.A_BOLD)
            elif (x, y) in carrot_cells:
                stdscr.addstr(cell_row, cell_col, "c", curses.color_pair(COLOR_CARROT))
            else:
                stdscr.addstr(cell_row, cell_col, ".")
        stdscr.addstr(row_offset + 1 + y, w + 1, "#", curses.color_pair(COLOR_WALL))

    # Bottom wall
    stdscr.addstr(row_offset + h + 1, 0, wall_line, curses.color_pair(COLOR_WALL))

    # Legend
    legend_row = row_offset + h + 2
    stdscr.addstr(legend_row, 0, "  B = you   c = carrot (+10pts)   F = fox (lose a heart)")

    stdscr.refresh()


def _game_over_screen(stdscr: "curses.window", game: BunnyHopGame) -> bool:
    """Returns True if the player wants to restart."""
    stdscr.erase()
    msg1 = "GAME OVER!"
    msg2 = f"Final score: {game.score}  (Level {game.level})"
    msg3 = "Press R to restart or Q to quit."
    stdscr.addstr(2, 2, msg1, curses.A_BOLD)
    stdscr.addstr(3, 2, msg2)
    stdscr.addstr(5, 2, msg3)
    stdscr.nodelay(False)  # blocking wait for key
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return False
        if key in (ord("r"), ord("R")):
            return True


def main(stdscr: "curses.window") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(TICK_MS)
    _init_colors()

    while True:
        game = BunnyHopGame()

        while not game.game_over:
            _draw(stdscr, game)
            key = stdscr.getch()

            direction: str | None = None
            if key == curses.KEY_UP:
                direction = "UP"
            elif key == curses.KEY_DOWN:
                direction = "DOWN"
            elif key == curses.KEY_LEFT:
                direction = "LEFT"
            elif key == curses.KEY_RIGHT:
                direction = "RIGHT"
            elif key in (ord("q"), ord("Q")):
                return

            game.update(direction)

        if not _game_over_screen(stdscr, game):
            break

        # Reset for new game
        stdscr.nodelay(True)
        stdscr.timeout(TICK_MS)
