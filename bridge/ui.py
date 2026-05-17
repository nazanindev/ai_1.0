from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from bridge.bidding import Auction, Bid, Call, CallType, Strain, SEATS
from bridge.cards import Card, Suit
from bridge.play import Trick


# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_DARK = "\033[48;5;22m"   # dark green (felt)
    BG_NAVY = "\033[48;5;17m"
    BLACK   = "\033[30m"


_USE_COLOR = True


def set_color(enabled: bool) -> None:
    global _USE_COLOR
    _USE_COLOR = enabled


def _c(*codes: str) -> str:
    return "".join(codes) if _USE_COLOR else ""


def _r() -> str:
    return C.RESET if _USE_COLOR else ""


def suit_colored(symbol: str, is_red: bool) -> str:
    color = _c(C.BOLD, C.RED) if is_red else _c(C.BOLD, C.WHITE)
    return f"{color}{symbol}{_r()}"


def _fmt_suit(suit: Suit) -> str:
    return suit_colored(suit.symbol(), suit.is_red())


def _fmt_strain(strain: Strain) -> str:
    if strain == Strain.NOTRUMP:
        return f"{_c(C.BOLD, C.CYAN)}NT{_r()}"
    is_red = strain in (Strain.DIAMONDS, Strain.HEARTS)
    color = _c(C.BOLD, C.RED) if is_red else _c(C.BOLD, C.WHITE)
    return f"{color}{strain.symbol()}{_r()}"


def _fmt_card(card: Card) -> str:
    is_red = card.suit.is_red()
    color = _c(C.BOLD, C.RED) if is_red else _c(C.BOLD, C.WHITE)
    return f"{color}{card.rank.symbol()}{card.suit.symbol()}{_r()}"


def _fmt_bid(call: Call) -> str:
    if call.call_type != CallType.BID or call.bid is None:
        label = call.call_type.value
        color = _c(C.DIM, C.WHITE) if call.call_type == CallType.PASS else _c(C.BOLD, C.YELLOW)
        return f"{color}{label}{_r()}"
    b = call.bid
    return f"{_c(C.BOLD, C.WHITE)}{b.level}{_r()}{_fmt_strain(b.strain)}"


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
BANNER = r"""
  ██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗
  ██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝
  ██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗
  ██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝
  ██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗
  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝
"""


def print_banner() -> None:
    print(_c(C.BOLD, C.GREEN) + BANNER + _r())
    tagline = "  ♠ ♥  CONTRACT BRIDGE  ♦ ♣"
    print(_c(C.BOLD, C.YELLOW) + tagline.center(48) + _r())
    print()


# ---------------------------------------------------------------------------
# Hand display helpers
# ---------------------------------------------------------------------------
def _hand_by_suit(hand: List[Card]) -> Dict[Suit, List[Card]]:
    by_suit: Dict[Suit, List[Card]] = {s: [] for s in reversed(list(Suit))}
    for c in hand:
        by_suit[c.suit].append(c)
    for cards in by_suit.values():
        cards.sort(key=lambda c: c.rank, reverse=True)
    return by_suit


def _hand_lines(hand: List[Card], hide: bool = False) -> List[str]:
    """Return 4 lines (one per suit) for the hand."""
    by_suit = _hand_by_suit(hand)
    lines = []
    for suit in reversed(list(Suit)):
        cards = by_suit[suit]
        suit_str = _fmt_suit(suit)
        if hide:
            pips = " ".join(["▪"] * len(cards))
            dim = _c(C.DIM, C.WHITE)
            lines.append(f"{suit_str} {dim}{pips}{_r()}")
        else:
            pips = " ".join(_fmt_card(c) for c in cards) if cards else f"{_c(C.DIM)}—{_r()}"
            lines.append(f"{suit_str} {pips}")
    return lines


def _box(lines: List[str], title: str = "", width: int = 34) -> List[str]:
    """Wrap lines in a Unicode box."""
    top = f"╔{'═' * width}╗"
    bot = f"╚{'═' * width}╝"
    result = []
    if title:
        pad = (width - len(title)) // 2
        title_line = f"╠{'═' * pad} {_c(C.BOLD, C.YELLOW)}{title}{_r()} {'═' * (width - pad - len(title) - 2)}╣"
        result.append(top)
        result.append(title_line)
    else:
        result.append(top)
    for line in lines:
        visible_len = len(_strip_ansi(line))
        padding = width - visible_len - 1
        result.append(f"║ {line}{' ' * padding}║")
    result.append(bot)
    return result


def _strip_ansi(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def _pad_to(s: str, width: int) -> str:
    visible = len(_strip_ansi(s))
    return s + " " * max(0, width - visible)


# ---------------------------------------------------------------------------
# Table layout
# ---------------------------------------------------------------------------
TABLE_WIDTH = 72


def _center_text(text: str, width: int = TABLE_WIDTH) -> str:
    visible = len(_strip_ansi(text))
    pad = (width - visible) // 2
    return " " * pad + text


def print_table(
    hands: Dict[str, List[Card]],
    current_seat: str,
    dummy_seat: Optional[str],
    trick: Optional[Trick],
    tricks_won: Dict[str, int],
    contract: Optional[Bid],
    declarer: Optional[str],
    vuln: bool,
) -> None:
    print()
    sep = _c(C.DIM, C.GREEN) + "─" * TABLE_WIDTH + _r()
    print(sep)

    # Contract / vulnerability info bar
    if contract and declarer:
        vul_str = (_c(C.RED) + "VUL" + _r()) if vuln else (_c(C.GREEN) + "NV" + _r())
        ns_tricks = tricks_won.get("N", 0) + tricks_won.get("S", 0)
        ew_tricks = tricks_won.get("E", 0) + tricks_won.get("W", 0)
        info = (
            f"  Contract: {_c(C.BOLD)}{contract.level}{_r()}{_fmt_strain(contract.strain)}"
            f"  Declarer: {_c(C.BOLD, C.CYAN)}{declarer}{_r()}"
            f"  {vul_str}"
            f"  NS: {_c(C.BOLD, C.GREEN)}{ns_tricks}{_r()} tricks"
            f"  EW: {_c(C.BOLD, C.RED)}{ew_tricks}{_r()} tricks"
        )
        print(info)
    print(sep)

    # North hand
    north_lines = _hand_lines(hands["N"], hide=("N" not in _visible_seats(current_seat, dummy_seat, declarer)))
    print(_center_text(_c(C.BOLD, C.CYAN) + "  ♦  NORTH  ♦  " + _r()))
    for line in north_lines:
        print(_center_text(line))
    print()

    # Middle row: West | Center | East
    west_lines = _hand_lines(hands["W"], hide=("W" not in _visible_seats(current_seat, dummy_seat, declarer)))
    east_lines = _hand_lines(hands["E"], hide=("E" not in _visible_seats(current_seat, dummy_seat, declarer)))

    center_lines = _center_panel(trick, contract)

    col_w = 22
    label_w = 6
    west_label  = _c(C.BOLD, C.CYAN) + "WEST" + _r()
    east_label  = _c(C.BOLD, C.CYAN) + "EAST" + _r()

    max_rows = max(len(west_lines), len(center_lines), len(east_lines))
    west_lines  += [""] * (max_rows - len(west_lines))
    center_lines += [""] * (max_rows - len(center_lines))
    east_lines  += [""] * (max_rows - len(east_lines))

    for i, (w, ctr, e) in enumerate(zip(west_lines, center_lines, east_lines)):
        label = west_label if i == 1 else "    "
        e_label = east_label if i == 1 else "    "
        wpad = _pad_to(w, col_w)
        cpad = _pad_to(ctr, 24)
        print(f"  {label} {wpad}  {cpad}  {e_label} {e}")

    print()

    # South hand
    south_lines = _hand_lines(hands["S"])
    print(_center_text(_c(C.BOLD, C.CYAN) + "  ♦  SOUTH (You)  ♦  " + _r()))
    for line in south_lines:
        print(_center_text(line))

    print(sep)


def _visible_seats(current: str, dummy: Optional[str], declarer: Optional[str]) -> set:
    visible = {"S"}
    if dummy:
        visible.add(dummy)
    return visible


def _center_panel(trick: Optional[Trick], contract: Optional[Bid]) -> List[str]:
    """Return lines for the center of the table showing current trick."""
    lines = []
    if trick is None or not trick.plays:
        lines.append(_c(C.DIM) + "  (no trick in progress)" + _r())
        return lines

    plays = {seat: card for seat, card in trick.plays}
    north = _fmt_card(plays["N"]) if "N" in plays else "  "
    south = _fmt_card(plays["S"]) if "S" in plays else "  "
    west  = _fmt_card(plays["W"]) if "W" in plays else "  "
    east  = _fmt_card(plays["E"]) if "E" in plays else "  "

    lines.append("        " + north)
    lines.append(f"  {west}   ╋   {east}")
    lines.append("        " + south)
    return lines


# ---------------------------------------------------------------------------
# Bidding display
# ---------------------------------------------------------------------------
def print_auction(auction: Auction) -> None:
    print()
    header_cols = [f"{_c(C.BOLD, C.YELLOW)}{s:^8}{_r()}" for s in SEATS]
    print("  " + "".join(header_cols))
    print("  " + _c(C.DIM) + "─" * 32 + _r())

    # Pad calls so they start at dealer column
    dealer_idx = SEATS.index(auction.dealer)
    row: List[str] = ["        "] * dealer_idx
    for seat, call in auction.calls:
        row.append(f"{_fmt_bid(call):^8}")
        if len(row) % 4 == 0:
            print("  " + "".join(row))
            row = []
    if row:
        print("  " + "".join(row))
    print()


# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------
def print_scoreboard(scores: Dict[str, int], deals_played: int) -> None:
    print()
    print(_c(C.BOLD, C.GREEN) + "  ╔══════════════════════════════╗" + _r())
    print(_c(C.BOLD, C.GREEN) + "  ║       FINAL SCOREBOARD       ║" + _r())
    print(_c(C.BOLD, C.GREEN) + "  ╠══════════════════════════════╣" + _r())
    ns = scores.get("NS", 0)
    ew = scores.get("EW", 0)
    ns_color = C.GREEN if ns >= ew else C.RED
    ew_color = C.GREEN if ew > ns else C.RED
    print(f"  {_c(C.BOLD, C.GREEN)}║{_r()}  NS (You & North)  {_c(C.BOLD, ns_color)}{ns:>6}{_r()}  {_c(C.BOLD, C.GREEN)}║{_r()}")
    print(f"  {_c(C.BOLD, C.GREEN)}║{_r()}  EW (Opponents)    {_c(C.BOLD, ew_color)}{ew:>6}{_r()}  {_c(C.BOLD, C.GREEN)}║{_r()}")
    print(_c(C.BOLD, C.GREEN) + "  ╠══════════════════════════════╣" + _r())
    winner = "NS (You win!)" if ns > ew else ("EW (They win)" if ew > ns else "  Tie game!")
    w_color = C.YELLOW if ns == ew else (C.GREEN if ns > ew else C.RED)
    print(f"  {_c(C.BOLD, C.GREEN)}║{_r()}  {_c(C.BOLD, w_color)}{winner:<28}{_r()}  {_c(C.BOLD, C.GREEN)}║{_r()}")
    print(_c(C.BOLD, C.GREEN) + "  ╚══════════════════════════════╝" + _r())
    print()


def prompt_card_choice(hand: List[Card], trick: Trick) -> Card:
    from bridge.play import legal_plays
    legal = legal_plays(hand, trick)

    print(f"\n  {_c(C.BOLD)}Your hand:{_r()}")
    for i, card in enumerate(legal):
        print(f"    [{_c(C.BOLD, C.YELLOW)}{i + 1}{_r()}] {_fmt_card(card)}")
    print()

    while True:
        raw = input(f"  {_c(C.BOLD, C.CYAN)}Choose card (1–{len(legal)}): {_r()}").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(legal):
            return legal[int(raw) - 1]
        print(f"  {_c(C.RED)}Invalid choice.{_r()}")


def prompt_bid_choice(auction: Auction) -> Call:
    legal = auction.legal_bids()
    can_pass = True
    can_double = auction.can_double()
    can_redouble = auction.can_redouble()

    print(f"\n  {_c(C.BOLD)}Your bid (legal options):{_r()}")
    options: List[Tuple[str, Call]] = []
    idx = 1

    options.append((str(idx), Call.pass_call()))
    print(f"    [{_c(C.BOLD, C.YELLOW)}{idx}{_r()}] Pass")
    idx += 1

    if can_double:
        options.append((str(idx), Call.double()))
        print(f"    [{_c(C.BOLD, C.YELLOW)}{idx}{_r()}] Double")
        idx += 1
    if can_redouble:
        options.append((str(idx), Call.redouble()))
        print(f"    [{_c(C.BOLD, C.YELLOW)}{idx}{_r()}] Redouble")
        idx += 1

    for bid in legal:
        options.append((str(idx), Call(CallType.BID, bid)))
        print(f"    [{_c(C.BOLD, C.YELLOW)}{idx}{_r()}] {_fmt_strain(bid.strain)} {bid.level}{_fmt_strain(bid.strain)}")
        idx += 1

    print()
    while True:
        raw = input(f"  {_c(C.BOLD, C.CYAN)}Choose (1–{len(options)}): {_r()}").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][1]
        print(f"  {_c(C.RED)}Invalid choice.{_r()}")
