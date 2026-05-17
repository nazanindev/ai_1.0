from __future__ import annotations
import argparse
import random
import sys

from bridge import ui
from bridge.game import play_deal


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bridge",
        description="Contract Bridge — CLI card game",
    )
    parser.add_argument(
        "--deals", "-n",
        type=int,
        default=4,
        metavar="N",
        help="Number of deals to play (default: 4)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible deals",
    )
    parser.add_argument(
        "--vulnerable",
        action="store_true",
        help="Start with both sides vulnerable",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    args = parser.parse_args()

    if args.no_color:
        ui.set_color(False)

    ui.print_banner()

    print(f"  Playing {args.deal if hasattr(args, 'deal') else args.deals} deals")
    if args.seed is not None:
        print(f"  Seed: {args.seed}")
    print(f"  Vulnerability: {'Both' if args.vulnerable else 'None'}")
    print()
    input("  Press Enter to begin...")

    total_scores = {"NS": 0, "EW": 0}
    deals_played = 0
    rng = random.Random(args.seed)

    for deal_num in range(args.deals):
        deal_seed = rng.randint(0, 2**32) if args.seed is not None else None
        score, passed_out = play_deal(
            seed=deal_seed,
            vulnerable=args.vulnerable,
            deal_num=deal_num,
        )
        deals_played += 1

        if score > 0:
            total_scores["NS"] += score
        elif score < 0:
            total_scores["EW"] += (-score)

        print(f"\n  Running totals — NS: {total_scores['NS']}  EW: {total_scores['EW']}")

        if deal_num < args.deals - 1:
            again = input("\n  Next deal? [Enter / q to quit]: ").strip().lower()
            if again == "q":
                break

    ui.print_scoreboard(total_scores, deals_played)
