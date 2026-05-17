# ♠ ♥ Contract Bridge ♦ ♣

A colorful, feature-rich CLI implementation of Contract Bridge — the classic four-player trick-taking card game.

## How to Run

```bash
python -m bridge
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--deals N` / `-n N` | 4 | Number of deals to play |
| `--seed N` | random | Fixed seed for reproducible hands |
| `--vulnerable` | off | Start with both sides vulnerable |
| `--no-color` | off | Disable ANSI color output |

**Examples:**

```bash
python -m bridge --deals 6           # play 6 deals
python -m bridge --seed 42           # reproducible game
python -m bridge --vulnerable        # vulnerable scoring
python -m bridge --no-color          # plain text mode
```

## Rules Summary

Bridge is played by four players in two partnerships: **North-South** (you play South) vs **East-West** (AI opponents).

### The Deal
- 52-card deck, dealt 13 cards to each player.
- Seats are labeled N, E, S, W (compass points).

### The Auction
- Starting with the dealer, players take turns making **calls**:
  - **Bid**: level (1–7) + strain (♣ ♦ ♥ ♠ NT). Higher level or strain beats lower.
  - **Pass**: no bid.
  - **Double**: challenge the opponents' last bid.
  - **Redouble**: re-challenge after a double.
- Auction ends after **three consecutive passes** following a bid, or four passes at the start.
- The partnership that made the highest bid wins the **contract**. The player on that side who **first bid the contract's strain** is the **declarer**.

### The Play
- The player to the left of declarer leads the first card.
- **Dummy** (declarer's partner) lays their hand face-up on the table.
- Declarer plays both their own hand and dummy's hand.
- Players must **follow suit** if possible; otherwise they may play any card.
- **Trump suit** (the contract's strain, if not NT) beats all other suits.
- The highest card of the **led suit** wins the trick, unless trumped.
- Winner of each trick leads the next.

### Scoring
Duplicate-style scoring:

| Contract | Value |
|----------|-------|
| Minor (♣/♦) | 20 per trick |
| Major (♥/♠) | 30 per trick |
| NT | 40 first trick, 30 thereafter |
| Game bonus (trick score ≥ 100) | 300 non-vul / 500 vul |
| Small slam (level 6) | +500 non-vul / +750 vul |
| Grand slam (level 7) | +1000 non-vul / +1500 vul |

Overtricks score at the suit/NT rate (or high penalties if doubled/redoubled).

Undertricks: 50/trick (non-vul), 100/trick (vul) undoubled. See scoring module for doubled/redoubled tables.

## AI Bidding Conventions

The AI (N, E, W) uses basic **Standard American**-style point-count bidding:

- Opens **1NT** with 15–17 HCP and a balanced hand (4-3-3-3, 4-4-3-2, or 5-3-3-2).
- Opens **1 of a suit** (longest suit, higher-ranked if tied) with 13+ total points.
- Responds with raises or NT bids based on HCP and fit.
- Passes with < 13 points or no suitable call.

## Table Layout

```
  ────────────────────────────────────────────────────────────────────────
  Contract: 4♠  Declarer: S  NV  NS: 8 tricks  EW: 5 tricks
  ────────────────────────────────────────────────────────────────────────

                    ♦  NORTH  ♦
                    ♠ ▪ ▪ ▪ ▪
                    ♥ ▪ ▪ ▪
                    ♦ ▪ ▪ ▪
                    ♣ ▪ ▪ ▪

  WEST  ♠ ▪ ▪ ▪         ♠5         EAST  ♠ ▪ ▪ ▪
        ♥ ▪ ▪      ♥J  ╋  ♥Q             ♥ ▪ ▪
        ♦ ▪ ▪           ♣9              ♦ ▪ ▪
        ♣ ▪ ▪                           ♣ ▪

                    ♦  SOUTH (You)  ♦
                    ♠ A K Q T 9
                    ♥ A K 5
                    ♦ K Q J
                    ♣ 4 2
  ────────────────────────────────────────────────────────────────────────
```

Cards are color-coded: **red** for ♥ ♦, **white** for ♠ ♣. Opponent and North's hidden cards show as ▪ dots; dummy's hand is revealed during play.
