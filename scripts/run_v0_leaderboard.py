import argparse
import sys
from pathlib import Path

import pandas as pd
from pybaseball import playerid_reverse_lookup

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from counterpunch.buckets import add_attack_buckets
from counterpunch.loss_events import add_loss_flags
from counterpunch.metric import (
    find_counterpunch_opportunities,
    score_opportunities,
    summarize_hitter_scores,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run Counterpunch Index v0.2 leaderboard.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--min-opportunities", type=int, default=100)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output")
    return parser.parse_args()


def add_hitter_names(leaderboard):
    if leaderboard.empty:
        return leaderboard

    ids = leaderboard["batter"].dropna().astype(int).unique().tolist()
    names = playerid_reverse_lookup(ids, key_type="mlbam")
    names = names[["key_mlbam", "name_first", "name_last"]].copy()
    names["hitter_name"] = names["name_first"] + " " + names["name_last"]

    leaderboard = leaderboard.merge(
        names[["key_mlbam", "hitter_name"]],
        left_on="batter",
        right_on="key_mlbam",
        how="left",
    ).drop(columns=["key_mlbam"])

    cols = ["batter", "hitter_name"] + [
        col for col in leaderboard.columns if col not in {"batter", "hitter_name"}
    ]
    return leaderboard[cols]


def format_leaderboard(leaderboard, start, end, min_opportunities, threshold):
    leaderboard = leaderboard.copy().reset_index(drop=True)
    leaderboard.insert(0, "rank", leaderboard.index + 1)
    leaderboard.insert(1, "date_start", start)
    leaderboard.insert(2, "date_end", end)
    leaderboard.insert(3, "min_opportunities", min_opportunities)
    leaderboard.insert(4, "location_threshold", threshold)

    cols = [
        "rank",
        "date_start",
        "date_end",
        "min_opportunities",
        "location_threshold",
        "batter",
        "hitter_name",
        "opportunities",
        "counterpunch_index",
        "repeat_delta_run_exp",
        "baseline_delta_run_exp",
    ]
    return leaderboard[cols]


def main():
    args = parse_args()

    df = pd.read_csv(args.input_csv).reset_index(drop=True)
    start = str(df["game_date"].min()) if "game_date" in df.columns else "unknown"
    end = str(df["game_date"].max()) if "game_date" in df.columns else "unknown"

    df = add_attack_buckets(df)
    df = add_loss_flags(df)

    print("Finding opportunities...", flush=True)
    opportunities = find_counterpunch_opportunities(df, threshold=args.threshold)
    print(f"Found opportunities: {len(opportunities)}", flush=True)

    scores = score_opportunities(
        df,
        opportunities,
        threshold=args.threshold,
        show_progress=True,
    )
    hitter_scores = summarize_hitter_scores(scores)

    if hitter_scores.empty:
        print("No matched opportunities found.")
        return

    leaderboard = hitter_scores[hitter_scores["opportunities"] >= args.min_opportunities]
    leaderboard = leaderboard.sort_values("counterpunch_index", ascending=False)
    leaderboard = add_hitter_names(leaderboard)
    leaderboard = format_leaderboard(
        leaderboard,
        start,
        end,
        args.min_opportunities,
        args.threshold,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        leaderboard.to_csv(output_path, index=False)

    print(f"Date range: {start} to {end}")
    print(f"Input CSV: {args.input_csv}")
    print(f"Matched opportunities: {len(opportunities)}")
    print(f"Minimum opportunities: {args.min_opportunities}")
    print(f"Location threshold: {args.threshold}")
    print(f"Qualified hitters: {len(leaderboard)}")
    if args.output:
        print(f"Output: {args.output}")
    print("\nLeaderboard:")
    print(leaderboard.head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()
