from __future__ import annotations
import random
from typing import Dict, List, Optional, Tuple

from bridge.bidding import (
    Auction, Bid, Call, CallType, PARTNERS, PARTNERSHIPS, SEATS,
    simple_ai_bid,
)
from bridge.cards import Card, Deck, Suit
from bridge.play import Trick, legal_plays, simple_ai_play
from bridge.scoring import score_contract
from bridge import ui


def play_deal(
    seed: Optional[int],
    vulnerable: bool,
    deal_num: int,
) -> Tuple[int, bool]:
    """Play one complete deal. Returns (score, passed_out)."""
    deck = Deck(seed=seed)
    hands = deck.deal()

    dealer = SEATS[deal_num % 4]
    auction = Auction(dealer)

    # -----------------------------------------------------------------------
    # Auction phase
    # -----------------------------------------------------------------------
    print(f"\n  Dealer: {dealer}  |  Deal #{deal_num + 1}")
    print()

    while not auction.is_finished():
        seat = auction.current_seat
        ui.print_auction(auction)

        if seat == "S":
            # Human player bids
            ui.print_table(
                hands, seat, None, None,
                {"N": 0, "E": 0, "S": 0, "W": 0},
                None, None, vulnerable,
            )
            call = ui.prompt_bid_choice(auction)
        else:
            call = simple_ai_bid(hands[seat], auction)
            print(f"  {seat} bids: {call}")

        auction.make_call(call)

    ui.print_auction(auction)

    if auction.passed_out():
        print("  All four players passed — hand passed out.")
        return 0, True

    contract = auction.current_contract
    declarer = auction.declarer()
    assert contract is not None and declarer is not None

    dummy_seat = PARTNERS[declarer]
    print(f"\n  Contract: {contract}  Declarer: {declarer}  Dummy: {dummy_seat}")

    # -----------------------------------------------------------------------
    # Play phase
    # -----------------------------------------------------------------------
    trump_suit = contract.strain.as_suit()
    lead_seat = SEATS[(SEATS.index(declarer) + 1) % 4]

    tricks_won: Dict[str, int] = {"N": 0, "E": 0, "S": 0, "W": 0}
    trick_num = 0

    current_lead = lead_seat

    while trick_num < 13:
        trick = Trick(trump=trump_suit, lead_seat=current_lead)

        seats_in_order = [SEATS[(SEATS.index(current_lead) + i) % 4] for i in range(4)]

        for seat in seats_in_order:
            ui.print_table(
                hands, seat, dummy_seat, trick,
                {
                    "N": tricks_won["N"],
                    "E": tricks_won["E"],
                    "S": tricks_won["S"],
                    "W": tricks_won["W"],
                },
                contract, declarer, vulnerable,
            )

            # Determine who actually controls this seat's card
            if seat == "S":
                card = ui.prompt_card_choice(hands[seat], trick)
            elif seat == dummy_seat and (declarer == "S" or dummy_seat == "S"):
                # Player controls dummy when playing as declarer or dummy is S
                print(f"\n  Playing dummy ({seat}):")
                card = ui.prompt_card_choice(hands[seat], trick)
            else:
                card = simple_ai_play(hands[seat], trick, contract)
                print(f"  {seat} plays: {card}")

            hands[seat].remove(card)
            trick.plays.append((seat, card))

        winner = trick.winner()
        tricks_won[winner] += 1
        print(f"\n  Trick {trick_num + 1} won by {winner} with {trick.winning_card()}")
        trick_num += 1
        current_lead = winner

    ns_tricks = tricks_won["N"] + tricks_won["S"]
    ew_tricks = tricks_won["E"] + tricks_won["W"]

    declarer_side = PARTNERSHIPS[declarer]
    tricks_made = ns_tricks if declarer_side == "NS" else ew_tricks

    result = score_contract(
        contract,
        tricks_made,
        auction.doubled,
        auction.redoubled,
        vulnerable,
    )

    # Adjust sign: positive = NS
    if declarer_side == "EW":
        result = -result

    print(f"\n  Result: {tricks_made} tricks made (needed {contract.tricks_needed()})")
    diff = tricks_made - contract.tricks_needed()
    if diff >= 0:
        print(f"  Contract made {'exactly' if diff == 0 else f'+{diff}'}!")
    else:
        print(f"  Contract down {-diff}.")
    print(f"  Score: NS {'+' if result >= 0 else ''}{result}")

    return result, False
