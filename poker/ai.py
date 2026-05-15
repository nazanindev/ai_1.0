from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poker.player import Player
    from poker.game import GameState


# Preflop hand strength table (Chen formula approximation, simplified)
# Maps (rank_val_1, rank_val_2, suited) -> strength 0-10
def _preflop_strength(p: Player) -> float:
    if len(p.hole_cards) < 2:
        return 0.0
    r1, r2 = sorted([c.rank.value for c in p.hole_cards], reverse=True)
    suited = p.hole_cards[0].suit == p.hole_cards[1].suit

    # Pairs
    if r1 == r2:
        return min(10.0, r1 / 2.0 + 5)

    # High card component (aces = 14)
    base = r1 / 2.0
    # Gap penalty
    gap = r1 - r2
    gap_penalty = [0, 0, 1, 2, 4, 5][min(gap, 5)]
    # Suited bonus
    suited_bonus = 2.0 if suited else 0.0
    # Connectedness bonus
    conn_bonus = 1.0 if gap == 1 else 0.0

    strength = base - gap_penalty + suited_bonus + conn_bonus
    return max(0.0, min(10.0, strength))


def _postflop_strength(p: Player, community: list) -> float:
    """Quick hand eval score normalized to 0-10."""
    from poker.hand_eval import evaluate, ROYAL_FLUSH
    if not community or len(p.hole_cards) < 2:
        return _preflop_strength(p)
    score, _ = evaluate(p.hole_cards + community)
    # score[0] is hand category 0-9
    return score[0] / 9.0 * 10.0


def decide_action(
    player: Player,
    state: GameState,
    options: list[str],
    aggressiveness: float = 0.5,
) -> str:
    """
    Simple heuristic AI.
    aggressiveness 0.0 = tight/passive, 1.0 = loose/aggressive.
    """
    community = state.community
    if community:
        strength = _postflop_strength(player, community)
    else:
        strength = _preflop_strength(player)

    # Add noise so bots are unpredictable
    strength += random.uniform(-1.5, 1.5)
    strength = max(0.0, min(10.0, strength))

    to_call = next(
        (int(o.split()[1]) for o in options if o.startswith("call")), 0
    )
    pot = state.pot
    pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 0.0

    # Thresholds adjusted by aggressiveness
    fold_thresh = 2.5 - aggressiveness * 1.5      # fold below this
    call_thresh = 5.0 - aggressiveness * 1.5      # raise above this

    if strength < fold_thresh:
        # Fold unless free (can check)
        if "check" in options:
            return "check"
        return "fold"

    if strength >= call_thresh and "raise" in options:
        # Raise: size to 2-3x big blind or pot-based
        raise_amount = int(pot * (0.5 + aggressiveness * 0.5)) + to_call
        # Clamp to what player can afford
        raise_amount = min(raise_amount, player.chips)
        return f"raise {raise_amount}"

    # Call or check
    if "check" in options:
        return "check"
    if to_call <= player.chips:
        return f"call {to_call}"
    return "fold"
