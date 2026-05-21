import argparse
import sys
from pathlib import Path

import pandas as pd
from pybaseball import playerid_reverse_lookup, statcast

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
    parser.add_argument("--season", type=int)
    parser.add_argument("--start", default="2024-04-01")
    parser.add_argument("--end", default="2024-04-07")
    parser.add_argument("--min-opportunities", type=int, default=10)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output")
    parser.add_argument("--input-csv")
    parser.add_argument(
        "--location-mode",
        choices=["bucket", "proximity"],
        default="bucket",
    )
    parser.add_argument("--location-threshold", type=float, default=0.5)
    return parser.parse_args()


def date_range_from_args(args):
    if args.season:
        return f"{args.season}-03-01", f"{args.season}-11-30"
    return args.start, args.end


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


def format_leaderboard(
    leaderboard,
    start,
    end,
    min_opportunities,
    location_mode,
    location_threshold,
):
    leaderboard = leaderboard.copy().reset_index(drop=True)
    leaderboard.insert(0, "rank", leaderboard.index + 1)
    leaderboard.insert(1, "date_start", start)
    leaderboard.insert(2, "date_end", end)
    leaderboard.insert(3, "min_opportunities", min_opportunities)
    leaderboard.insert(4, "location_mode", location_mode)
    leaderboard.insert(5, "location_threshold", location_threshold)

    cols = [
        "rank",
        "date_start",
        "date_end",
        "min_opportunities",
        "location_mode",
        "location_threshold",
        "batter",
        "hitter_name",
        "opportunities",
        "counterpunch_index",
        "repeat_delta_run_exp",
        "baseline_delta_run_exp",
    ]
    return leaderboard[cols]


def load_statcast_data(args):
    if args.input_csv:
        df = pd.read_csv(args.input_csv)
        if "game_date" in df.columns:
            start = str(df["game_date"].min())
            end = str(df["game_date"].max())
        else:
            start, end = date_range_from_args(args)
        return df.reset_index(drop=True), start, end

    start, end = date_range_from_args(args)
    df = statcast(start_dt=start, end_dt=end)
    return df.reset_index(drop=True), start, end


def main():
    args = parse_args()

    df, start, end = load_statcast_data(args)
    df = add_attack_buckets(df)
    df = add_loss_flags(df)

    opportunities = find_counterpunch_opportunities(
        df,
        location_mode=args.location_mode,
        location_threshold=args.location_threshold,
    )
    baseline_columns = ["batter", "attack_bucket"]
    if args.location_mode == "proximity":
        baseline_columns = ["batter", "pitch_group", "count_bucket"]
    scores = score_opportunities(df, opportunities, baseline_columns=baseline_columns)
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
        args.location_mode,
        args.location_threshold,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        leaderboard.to_csv(output_path, index=False)

    print(f"Date range: {start} to {end}")
    if args.input_csv:
        print(f"Input CSV: {args.input_csv}")
    print(f"Matched opportunities: {len(opportunities)}")
    print(f"Minimum opportunities: {args.min_opportunities}")
    print(f"Location mode: {args.location_mode}")
    if args.location_mode == "proximity":
        print(f"Location threshold: {args.location_threshold}")
    print(f"Qualified hitters: {len(leaderboard)}")
    if args.output:
        print(f"Output: {args.output}")
    print("\nLeaderboard:")
    print(leaderboard.head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()
