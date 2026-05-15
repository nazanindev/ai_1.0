"""In-game tutorial and quick-reference instructions for Pai Gow Tiles."""
from .tiles import PAIR_RANKING

_SEP = "=" * 52


def _page(text: str) -> None:
    print()
    print(_SEP)
    print(text)
    print(_SEP)
    try:
        input("  Press Enter to continue...")
    except EOFError:
        pass


def show_tutorial() -> None:
    _page("""\
  PAI GOW TILES — TUTORIAL  (1/7)
  ================================
  Pai Gow Tiles is an ancient Chinese gambling game
  played with a set of 32 Chinese dominoes (tiles).
  It is a staple at Asian casinos — you'll find it
  in a quiet corner of the floor, usually populated
  by older players and backed by quiet concentration.

  Goal: split your 4 tiles into two 2-tile hands and
  beat the banker's two hands. Beat BOTH to win.
  Win only one? That's a push. Lose both? You lose.""")

    _page("""\
  THE 32-TILE DECK  (2/7)
  ========================
  The deck has 32 tiles, forming 16 "pairs":

  Civil pairs (11) — each tile appears twice in deck:
    Teen [6:6]  Day [1:1]  Yan [4:4]  Gor [1:3]
    Mooy [1:5]  Chong [5:6]  Bon [4:6]  Foo [1:6]
    Ping [2:6]  Tit [2:5]  Look [3:6]

  Military pairs (5) — different tiles, matched rank:
    Gee Joon: [2:4]+[1:2]  (the supreme pair!)
    Mixed 9:  [1:8]+[4:5]
    Mixed 8:  [3:5]+[2:6]
    Mixed 7:  [1:6]+[2:5]
    Mixed 5:  [1:4]+[2:3]

  Tile display format: [top:bottom] pip counts.""")

    _page("""\
  SPLITTING YOUR 4 TILES  (3/7)
  ==============================
  After you are dealt 4 tiles, you MUST split them
  into two hands:
    • HIGH hand (back)  — your stronger hand
    • LOW hand  (front) — your weaker hand

  The high hand must be >= the low hand.
  (You cannot put a stronger hand up front.)

  You choose which two tiles go into your HIGH hand
  by entering their index numbers (1-4).
  The remaining two automatically become your LOW hand.

  Example: "1 3" puts tiles #1 and #3 in the HIGH
  hand, and tiles #2 and #4 in the LOW hand.""")

    _page("""\
  HAND VALUE — MOD 10  (4/7)
  ===========================
  A non-pair hand's strength is the total pip count
  of both tiles, modulo 10 (keep only the last digit):

    [4:6] + [5:6] = 21 pips  →  value = 1
    [3:6] + [1:5] = 15 pips  →  value = 5
    [6:6] + [3:6] = 21 pips  →  value = 1

  The highest possible non-pair value is 9, called
  "Gong" (九). A value of 0 is the worst.

  Special: Gee Joon tiles ([2:4] and [1:2]) count as
  either 3 or 6 pips each — whichever gives a better
  hand. The game picks the best value automatically.""")

    _page("""\
  PAIRS vs NON-PAIRS  (5/7)
  ==========================
  ANY pair ALWAYS beats ANY non-pair hand.

  When two players both have pairs, the higher-ranked
  pair wins. Pair ranking from best to worst:

    1. Gee Joon  2. Teen   3. Day   4. Yan
    5. Gor       6. Mooy   7. Chong 8. Bon
    9. Foo      10. Ping  11. Tit  12. Look
   13. Mixed 9  14. Mixed 8  15. Mixed 7  16. Mixed 5

  When two non-pair hands have the same value (a tie),
  the BANKER wins — this is called a "copy".""")

    _page("""\
  BANKER COMPARISON  (6/7)
  =========================
  After you split, the BANKER also splits their 4 tiles
  following the "house way" — a fixed strategy the
  casino uses. You never choose for the banker.

  Then:
    • Your HIGH hand vs Banker's HIGH hand
    • Your LOW  hand vs Banker's LOW  hand

  You need to win BOTH comparisons to win the round.
  Win one, lose one  →  push (bet returned).
  Lose both          →  you lose your bet.""")

    _page("""\
  COMMISSION  (7/7)
  ==================
  When you WIN a round, the house takes a 5% commission
  on your winnings. So a $100 bet that wins pays $95.

  This is the casino's edge. Over time it adds up, but
  smart splitting keeps it tight!

  CONTROLS SUMMARY:
    Startup:  [t] tutorial  [i] instructions
              [p] play       [q] quit
    In-game:  enter "1 3" to pick HIGH hand tiles
              [?] to show quick-reference
              [q] to cash out

  You are ready to play! Good luck.""")


def show_instructions() -> None:
    print()
    print(_SEP)
    print("  PAI GOW TILES — QUICK REFERENCE")
    print(_SEP)
    print("  GOAL:  Split 4 tiles into HIGH (back) + LOW (front) hands.")
    print("         Beat banker's HIGH AND LOW hands to win.")
    print("         Win only one → push.  Lose both → lose bet.")
    print()
    print("  HAND VALUE:  (pip1 + pip2) mod 10  (range 0-9; 9 is best)")
    print("  PAIRS:       Always beat non-pairs. Ranked as below.")
    print("  TIES:        Banker wins exact ties ('copy' rule).")
    print("  COMMISSION:  5% taken from winnings on a win.")
    print()
    print("  PAIR RANKINGS (best → worst):")
    for i, name in enumerate(PAIR_RANKING, 1):
        print(f"    {i:2d}. {name}")
    print()
    print("  CONTROLS:  enter two tile numbers for HIGH hand (e.g. '1 3')")
    print("             '?' = this screen   'q' = cash out")
    print(_SEP)
