from dataclasses import dataclass, field


@dataclass
class Bunny:
    x: int
    y: int
    lives: int = 3
    invincible_ticks: int = 0  # brief grace period after being hit

    def move(self, dx: int, dy: int, width: int, height: int) -> None:
        self.x = max(0, min(width - 1, self.x + dx))
        self.y = max(0, min(height - 1, self.y + dy))

    def tick_invincibility(self) -> None:
        if self.invincible_ticks > 0:
            self.invincible_ticks -= 1

    @property
    def is_invincible(self) -> bool:
        return self.invincible_ticks > 0


@dataclass
class Carrot:
    x: int
    y: int


@dataclass
class Fox:
    x: int
    y: int

    def step_toward(self, tx: int, ty: int, width: int, height: int) -> None:
        dx = 0 if tx == self.x else (1 if tx > self.x else -1)
        dy = 0 if ty == self.y else (1 if ty > self.y else -1)
        # Move along the larger axis first (simple chase logic)
        if abs(tx - self.x) >= abs(ty - self.y):
            self.x = max(0, min(width - 1, self.x + dx))
        else:
            self.y = max(0, min(height - 1, self.y + dy))
