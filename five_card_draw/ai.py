from __future__ import annotations
import random
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from five_card_draw.player import Player
    from five_card_draw.game import GameState


def _hand_strength(player: Player) -> float:
    """Score the player's current 5-card hand, normalized 0–10."""
    from five_card_draw.hand_eval import evaluate, ROYAL_FLUSH
    if len(player.hand) < 5:
        return 0.0
    score, _ = evaluate(player.hand)
    # score[0] is hand category 0–9
    return score[0] / 9.0 * 10.0


def decide_action(
    player: Player,
    state: GameState,
    options: list[str],
    aggressiveness: float = 0.5,
) -> str:
    """
    Simple heuristic AI for betting decisions.
    aggressiveness 0.0 = tight/passive, 1.0 = loose/aggressive.
    """
    strength = _hand_strength(player)
    strength += random.uniform(-1.5, 1.5)
    strength = max(0.0, min(10.0, strength))

    to_call = next(
        (int(o.split()[1]) for o in options if o.startswith("call")), 0
    )
    pot = state.pot

    fold_thresh = 2.5 - aggressiveness * 1.5
    call_thresh = 5.0 - aggressiveness * 1.5

    if strength < fold_thresh:
        if "check" in options:
            return "check"
        return "fold"

    if strength >= call_thresh and "raise" in options:
        raise_amount = int(pot * (0.5 + aggressiveness * 0.5)) + to_call
        raise_amount = min(raise_amount, player.chips)
        return f"raise {raise_amount}"

    if "check" in options:
        return "check"
    if to_call <= player.chips:
        return f"call {to_call}"
    return "fold"


def decide_discard(player: Player) -> list[int]:
    """
    Return 0-based indices of cards to discard.
    Strategy: keep any rank appearing 2+ times; otherwise keep top 2 high cards.
    Also keep 4-to-a-flush or 4-to-a-straight if applicable.
    """
    hand = player.hand
    if not hand:
        return []

    counts = Counter(c.rank.value for c in hand)

    # Cards belonging to a pair/trips/quads — keep them
    keep_by_rank: set[int] = set()
    for i, c in enumerate(hand):
        if counts[c.rank.value] >= 2:
            keep_by_rank.add(i)

    if keep_by_rank:
        # Keep matched cards; discard the rest
        discard = [i for i in range(5) if i not in keep_by_rank]
        # Don't draw more than 3 unless we have nothing (keep at most 3 discards when holding a pair)
        # Exception: if holding trips, keep only 2 (draw 2)
        return discard

    # No pairs — check for 4-to-a-flush
    suit_groups: dict = {}
    for i, c in enumerate(hand):
        suit_groups.setdefault(c.suit, []).append(i)
    for indices in suit_groups.values():
        if len(indices) == 4:
            discard_idx = [i for i in range(5) if i not in indices]
            return discard_idx

    # Check for 4-to-a-straight (4 consecutive ranks)
    indexed_vals = sorted(enumerate(hand), key=lambda x: x[1].rank.value)
    vals = [c.rank.value for _, c in indexed_vals]
    orig_indices = [i for i, _ in indexed_vals]
    for start in range(len(vals) - 3):
        window = vals[start:start + 4]
        if window[-1] - window[0] == 3 and len(set(window)) == 4:
            keep_set = set(orig_indices[start:start + 4])
            discard_idx = [i for i in range(5) if i not in keep_set]
            return discard_idx

    # No promising structure — keep top 2 high cards, discard 3
    sorted_by_val = sorted(range(5), key=lambda i: hand[i].rank.value, reverse=True)
    keep = set(sorted_by_val[:2])
    return [i for i in range(5) if i not in keep]
