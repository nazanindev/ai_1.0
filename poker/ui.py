from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poker.cards import Card
    from poker.player import Player

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


# ── Card art ───────────────────────────────────────────────────────────────────

def render_card(card: Card | None, hidden: bool = False) -> list[str]:
    """Return 5-line card art."""
    if card is None or hidden:
        return [
            dim("┌─────┐"),
            dim("│") + "░░░░░" + dim("│"),
            dim("│") + "░░░░░" + dim("│"),
            dim("│") + "░░░░░" + dim("│"),
            dim("└─────┘"),
        ]
    from poker.cards import Suit
    is_red = card.suit in (Suit.HEARTS, Suit.DIAMONDS)
    color = _RED if is_red else _WHITE
    rs = card.rank.symbol
    rank_l = f"{color}{rs:<2}{_RESET}"
    rank_r = f"{color}{rs:>2}{_RESET}"
    suit_c = f"{color}{card.suit.value}{_RESET}"
    return [
        "┌─────┐",
        f"│{rank_l}   │",
        f"│  {suit_c}  │",
        f"│   {rank_r}│",
        "└─────┘",
    ]


def render_cards_row(cards: list[Card | None], hidden: bool = False) -> str:
    """Render a horizontal row of cards and return as a single string block."""
    if not cards:
        return ""
    lines_list = [render_card(c, hidden=hidden) for c in cards]
    rows = []
    for i in range(5):
        rows.append("  ".join(lines[i] for lines in lines_list))
    return "\n".join(rows)


# ── Title banner ───────────────────────────────────────────────────────────────

BANNER = f"""{_BOLD}{_YELLOW}
  ████████╗███████╗██╗  ██╗ █████╗ ███████╗
     ██╔══╝██╔════╝╚██╗██╔╝██╔══██╗██╔════╝
     ██║   █████╗   ╚███╔╝ ███████║███████╗
     ██║   ██╔══╝   ██╔██╗ ██╔══██║╚════██║
     ██║   ███████╗██╔╝ ██╗██║  ██║███████║
     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

  ██╗  ██╗ ██████╗ ██╗     ██████╗      ███████╗███╗   ███╗
  ██║  ██║██╔═══██╗██║     ██╔══██╗     ██╔════╝████╗ ████║
  ███████║██║   ██║██║     ██║  ██║     █████╗  ██╔████╔██║
  ██╔══██║██║   ██║██║     ██║  ██║     ██╔══╝  ██║╚██╔╝██║
  ██║  ██║╚██████╔╝███████╗██████╔╝     ███████╗██║ ╚═╝ ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝      ╚══════╝╚═╝     ╚═╝
{_RESET}"""


# ── Table renderer ─────────────────────────────────────────────────────────────

def _player_label(p: Player, is_dealer: bool, is_current: bool) -> str:
    marker = bold(yellow(" ◄ YOU")) if p.is_human else ""
    dealer_m = bold(cyan(" [D]")) if is_dealer else ""
    act_m = bold(green(" ← action")) if is_current else ""
    status = ""
    if p.folded:
        status = dim(" (folded)")
    elif p.all_in:
        status = bold(red(" ALL-IN"))
    return f"{bold(p.name)}{dealer_m}{marker}{act_m}{status}  {yellow(str(p.chips) + ' chips')}"


def render_table(
    players: list[Player],
    community: list[Card],
    pot: int,
    dealer_idx: int,
    current_idx: int | None,
    street: str,
    message: str = "",
) -> str:
    width = 72
    border = dim("═" * width)
    lines: list[str] = []

    lines.append(f"\n{dim('╔' + '═' * width + '╗')}")
    title = f"  {bold(cyan(street.upper()))}   {dim('pot:')} {yellow(bold(str(pot) + ' chips'))}"
    lines.append(dim("║") + title)
    lines.append(dim("║") + dim("─" * width))

    # Community cards
    if community:
        cc_block = render_cards_row(community)
        for row in cc_block.split("\n"):
            lines.append(dim("║") + "  " + row)
    else:
        lines.append(dim("║") + dim("  [ waiting for community cards ]"))

    lines.append(dim("║") + dim("─" * width))

    # Players
    for i, p in enumerate(players):
        is_dealer = i == dealer_idx
        is_current = i == current_idx
        lbl = _player_label(p, is_dealer, is_current)
        lines.append(dim("║") + "  " + lbl)

        # Show hole cards
        if p.hole_cards:
            show_hidden = not p.is_human and not p.folded
            card_block = render_cards_row(p.hole_cards, hidden=show_hidden)
            for row in card_block.split("\n"):
                lines.append(dim("║") + "    " + row)
        if p.current_bet > 0:
            lines.append(dim("║") + dim(f"    bet: {p.current_bet}"))
        lines.append(dim("║"))

    if message:
        lines.append(dim("║") + f"  {bold(message)}")
        lines.append(dim("║"))

    lines.append(dim("╚" + "═" * width + "╝"))
    return "\n".join(lines)


def render_showdown(
    players: list[Player],
    community: list[Card],
    results: list[tuple[Player, str, bool]],
    pot: int,
) -> str:
    """Render showdown screen showing all hands and winners."""
    width = 72
    lines: list[str] = []
    lines.append(f"\n{dim('╔' + '═' * width + '╗')}")
    lines.append(dim("║") + bold(yellow("  ★ SHOWDOWN ★")))
    lines.append(dim("║") + dim("─" * width))
    lines.append(dim("║") + f"  {dim('Community:')}  " + "  ".join(
        c.colored_str() for c in community
    ))
    lines.append(dim("║") + dim("─" * width))

    for p, hand_name, won in results:
        if p.folded:
            line = f"  {bold(p.name)}  {dim('folded')}"
        else:
            cards_str = "  ".join(c.colored_str() for c in p.hole_cards)
            win_mark = bold(green(" ✔ WIN")) if won else ""
            line = f"  {bold(p.name)}  [{cards_str}]  {cyan(hand_name)}{win_mark}"
        lines.append(dim("║") + line)

    lines.append(dim("║") + dim("─" * width))
    lines.append(dim("║") + f"  {yellow(bold('Pot: ' + str(pot) + ' chips'))}")
    lines.append(dim("╚" + "═" * width + "╝"))
    return "\n".join(lines)
