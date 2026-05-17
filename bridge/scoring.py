from __future__ import annotations
from bridge.bidding import Bid, Strain


def score_contract(
    bid: Bid,
    tricks_made: int,
    doubled: bool,
    redoubled: bool,
    vulnerable: bool,
) -> int:
    """Return the NS score (positive = NS win, negative = EW win)."""
    tricks_needed = bid.tricks_needed()
    overtricks = tricks_made - tricks_needed
    undertricks = tricks_needed - tricks_made

    multiplier = 4 if redoubled else (2 if doubled else 1)

    if undertricks > 0:
        return -_undertrick_penalty(undertricks, doubled, redoubled, vulnerable)

    # Base trick score
    trick_score = _trick_score(bid, tricks_needed, doubled, redoubled)

    # Bonus for game / part-score / slam
    bonus = _bonus(trick_score, bid.level, vulnerable)

    # Overtrick score
    ot_score = _overtrick_score(bid, overtricks, doubled, redoubled, vulnerable)

    # Doubled/redoubled insult bonus
    insult = 50 * (multiplier // 2) if doubled or redoubled else 0

    return trick_score + bonus + ot_score + insult


def _trick_score(bid: Bid, tricks_for_contract: int, doubled: bool, redoubled: bool) -> int:
    multiplier = 4 if redoubled else (2 if doubled else 1)
    strain = bid.strain
    if strain == Strain.NOTRUMP:
        # 40 for first trick, 30 for each subsequent
        raw = 40 + 30 * (bid.level - 1)
    elif strain in (Strain.HEARTS, Strain.SPADES):
        raw = 30 * bid.level
    else:
        raw = 20 * bid.level
    return raw * multiplier


def _bonus(trick_score: int, level: int, vulnerable: bool) -> int:
    game_bonus = 500 if vulnerable else 300
    if level == 7:
        return (1500 if vulnerable else 1000) + game_bonus  # grand slam + game
    if level == 6:
        return (750 if vulnerable else 500) + game_bonus    # small slam + game
    if trick_score >= 100:
        return game_bonus
    return 50  # part score


def _overtrick_score(
    bid: Bid, overtricks: int, doubled: bool, redoubled: bool, vulnerable: bool
) -> int:
    if overtricks <= 0:
        return 0
    if redoubled:
        rate = 400 if vulnerable else 200
        return overtricks * rate
    if doubled:
        rate = 200 if vulnerable else 100
        return overtricks * rate
    strain = bid.strain
    if strain == Strain.NOTRUMP or strain in (Strain.HEARTS, Strain.SPADES):
        return overtricks * 30
    return overtricks * 20


def _undertrick_penalty(undertricks: int, doubled: bool, redoubled: bool, vulnerable: bool) -> int:
    if not doubled and not redoubled:
        rate = 100 if vulnerable else 50
        return undertricks * rate

    multiplier = 2 if redoubled else 1

    if vulnerable:
        # 200 per undertrick doubled, doubled again if redoubled
        penalty = undertricks * 200
    else:
        # 100 first, 200 second and third, 300 thereafter (doubled)
        if undertricks == 1:
            penalty = 100
        elif undertricks == 2:
            penalty = 300
        elif undertricks == 3:
            penalty = 500
        else:
            penalty = 500 + (undertricks - 3) * 300

    return penalty * multiplier
