import random
from .entities import Bunny, Carrot, Fox

WIDTH = 20
HEIGHT = 10
CARROTS_PER_LEVEL = 5
INVINCIBLE_TICKS = 8  # grace period ticks after a fox collision

DIRECTION_DELTAS = {
    "UP":    (0, -1),
    "DOWN":  (0,  1),
    "LEFT":  (-1, 0),
    "RIGHT": (1,  0),
}


def _random_empty_cell(occupied: set[tuple[int, int]], width: int, height: int) -> tuple[int, int]:
    attempts = 0
    while attempts < 1000:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if (x, y) not in occupied:
            return x, y
        attempts += 1
    # Fallback: scan sequentially
    for y in range(height):
        for x in range(width):
            if (x, y) not in occupied:
                return x, y
    raise RuntimeError("Grid is completely full — cannot place entity")


class BunnyHopGame:
    def __init__(self) -> None:
        self.width = WIDTH
        self.height = HEIGHT
        self.score = 0
        self.level = 1
        self.carrots_collected = 0
        self.game_over = False
        self.level_up_flash = 0  # display ticks for level-up message

        cx, cy = WIDTH // 2, HEIGHT // 2
        self.bunny = Bunny(x=cx, y=cy)
        occupied = {(cx, cy)}

        self.carrots: list[Carrot] = []
        self._spawn_carrots(3, occupied)

        self.foxes: list[Fox] = []
        self._spawn_foxes(1, occupied)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _occupied_cells(self) -> set[tuple[int, int]]:
        cells: set[tuple[int, int]] = {(self.bunny.x, self.bunny.y)}
        cells.update((c.x, c.y) for c in self.carrots)
        cells.update((f.x, f.y) for f in self.foxes)
        return cells

    def _spawn_carrots(self, n: int, occupied: set[tuple[int, int]]) -> None:
        for _ in range(n):
            x, y = _random_empty_cell(occupied, self.width, self.height)
            self.carrots.append(Carrot(x=x, y=y))
            occupied.add((x, y))

    def _spawn_foxes(self, n: int, occupied: set[tuple[int, int]]) -> None:
        for _ in range(n):
            x, y = _random_empty_cell(occupied, self.width, self.height)
            self.foxes.append(Fox(x=x, y=y))
            occupied.add((x, y))

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    # ------------------------------------------------------------------
    # Main update — called once per player input or game tick
    # ------------------------------------------------------------------

    def update(self, direction: str | None) -> None:
        if self.game_over:
            return

        if self.level_up_flash > 0:
            self.level_up_flash -= 1

        # Move bunny
        if direction in DIRECTION_DELTAS:
            dx, dy = DIRECTION_DELTAS[direction]
            self.bunny.move(dx, dy, self.width, self.height)

        # Tick invincibility before collision check
        self.bunny.tick_invincibility()

        # Check carrot collection
        eaten = [c for c in self.carrots if c.x == self.bunny.x and c.y == self.bunny.y]
        for c in eaten:
            self.carrots.remove(c)
            self.score += 10
            self.carrots_collected += 1

        # Replenish carrots so there's always at least 1 on the board
        if not self.carrots:
            occ = self._occupied_cells()
            self._spawn_carrots(1, occ)

        # Level up every CARROTS_PER_LEVEL collected
        if self.carrots_collected >= self.level * CARROTS_PER_LEVEL:
            self.level += 1
            self.level_up_flash = 12
            occ = self._occupied_cells()
            # Add one more fox per new level
            self._spawn_foxes(1, occ)

        # Move foxes toward bunny (foxes move every other tick via level-speed gating)
        fox_speed = max(1, 4 - self.level)  # foxes move faster at higher levels
        if random.randint(0, fox_speed - 1) == 0:
            for fox in self.foxes:
                fox.step_toward(self.bunny.x, self.bunny.y, self.width, self.height)

        # Check fox collision
        if not self.bunny.is_invincible:
            hit = any(f.x == self.bunny.x and f.y == self.bunny.y for f in self.foxes)
            if hit:
                self.bunny.lives -= 1
                if self.bunny.lives <= 0:
                    self.game_over = True
                else:
                    self.bunny.invincible_ticks = INVINCIBLE_TICKS
