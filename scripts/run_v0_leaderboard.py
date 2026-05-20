import argparse
import sys
from pathlib import Path

from pybaseball import statcast

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from counterpunch.buckets import add_attack_buckets
from counterpunch.loss_events import add_loss_flags
from counterpunch.metric import (
    find_counterpunch_opportunities,
    score_opportunities,
    summarize_hitter_scores,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run Counterpunch Index v0 leaderboard.")
    parser.add_argument("--start", default="2024-04-01")
    parser.add_argument("--end", default="2024-04-07")
    parser.add_argument("--min-opportunities", type=int, default=10)
    parser.add_argument("--limit", type=int, default=25)
    return parser.parse_args()


def main():
    args = parse_args()

    df = statcast(start_dt=args.start, end_dt=args.end).reset_index(drop=True)
    df = add_attack_buckets(df)
    df = add_loss_flags(df)

    opportunities = find_counterpunch_opportunities(df)
    scores = score_opportunities(df, opportunities)
    hitter_scores = summarize_hitter_scores(scores)

    if hitter_scores.empty:
        print("No matched opportunities found.")
        return

    leaderboard = hitter_scores[hitter_scores["opportunities"] >= args.min_opportunities]
    leaderboard = leaderboard.sort_values("counterpunch_index", ascending=False)

    print(f"Date range: {args.start} to {args.end}")
    print(f"Matched opportunities: {len(opportunities)}")
    print(f"Minimum opportunities: {args.min_opportunities}")
    print(f"Qualified hitters: {len(leaderboard)}")
    print("\nLeaderboard:")
    print(leaderboard.head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()
