from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from five_card_draw.cards import Card
    from five_card_draw.player import Player

# ── ANSI palette ──────────────────────────────────────────────────────────────
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[91m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_CYAN = "\033[96m"
_WHITE = "\033[97m"
_BG_GREEN = "\033[42m"
_BG_BLACK = "\033[40m"


def red(s: str) -> str:
    return f"{_RED}{s}{_RESET}"


def green(s: str) -> str:
    return f"{_GREEN}{s}{_RESET}"


def yellow(s: str) -> str:
    return f"{_YELLOW}{s}{_RESET}"


def cyan(s: str) -> str:
    return f"{_CYAN}{s}{_RESET}"


def bold(s: str) -> str:
    return f"{_BOLD}{s}{_RESET}"


def dim(s: str) -> str:
    return f"{_DIM}{s}{_RESET}"


BANNER = f"""
{_BOLD}{_CYAN}
  ╔═══════════════════════════════════╗
  ║   5-Card Draw Poker — CLI         ║
  ╚═══════════════════════════════════╝
{_RESET}"""


def render_card(card: Card | None, hidden: bool = False) -> list[str]:
    """Return 5-line card art."""
    if card is None or hidden:
        return [
            "┌─────┐",
            "│░░░░░│",
            "│░░░░░│",
            "│░░░░░│",
            "└─────┘",
        ]
    return card.render_lines(hidden=False)


def _render_hand(cards: list[Card], hidden: bool = False) -> list[str]:
    """Render a row of up to 5 cards side-by-side (5 lines tall)."""
    if not cards:
        return ["  (no cards)"] + [""] * 4
    rendered = [render_card(c, hidden=hidden) for c in cards]
    rows: list[str] = []
    for row_idx in range(5):
        rows.append("  ".join(r[row_idx] for r in rendered))
    return rows


def render_table(
    players: list[Player],
    pot: int,
    current_idx: int | None,
    phase: str,
    message: str = "",
) -> str:
    width = 72
    lines: list[str] = []
    lines.append("╔" + "═" * width + "╗")
    phase_str = f"  {bold(phase)}   pot: {yellow(str(pot) + ' chips')}"
    lines.append("║  " + phase_str)
    lines.append("║  " + "─" * (width - 2))

    for idx, p in enumerate(players):
        is_current = idx == current_idx
        hidden = not p.is_human and not p.folded
        status = ""
        if p.folded:
            status = dim(" [folded]")
        elif p.all_in:
            status = cyan(" [all-in]")
        marker = f" {bold(cyan('◄ YOU'))} ← action" if (p.is_human and is_current) else (
            f" {bold(cyan('← action'))}" if is_current else ""
        )
        you_label = f" {bold(cyan('◄ YOU'))}" if p.is_human and not is_current else ""
        chips_str = dim(f"{p.chips} chips")
        header = f"  {bold(p.name)}{you_label}{marker}{status}  {chips_str}"
        lines.append("║" + header)

        hand_lines = _render_hand(p.hand, hidden=hidden and not p.folded)
        for hl in hand_lines:
            lines.append("║    " + hl)
        lines.append("║")

    if message:
        lines.append("║  " + bold(yellow(message)))
        lines.append("║")

    lines.append("╚" + "═" * width + "╝")
    return "\n".join(lines)


def render_showdown(
    players: list[Player],
    results: list[tuple[Player, str, bool]],
    pot: int,
) -> str:
    width = 72
    lines: list[str] = []
    lines.append("╔" + "═" * width + "╗")
    lines.append(f"║  {bold('SHOWDOWN')}   pot: {yellow(str(pot) + ' chips')}")
    lines.append("║  " + "─" * (width - 2))

    result_map = {p: (hand_name, won) for p, hand_name, won in results}
    for p in players:
        hand_name, won = result_map.get(p, ("folded", False))
        status = bold(green(" ★ WINNER")) if won else (dim(" [folded]") if p.folded else "")
        chips_str = dim(f"{p.chips} chips")
        lines.append(f"║  {bold(p.name)}{status}  {chips_str}")
        if not p.folded:
            lines.append(f"║    {cyan(hand_name)}")
            for hl in _render_hand(p.hand, hidden=False):
                lines.append("║    " + hl)
        lines.append("║")

    lines.append("╚" + "═" * width + "╝")
    return "\n".join(lines)
