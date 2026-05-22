import argparse
import sys
from pathlib import Path

from pybaseball import playerid_reverse_lookup, statcast_batter

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from counterpunch.buckets import add_attack_buckets
from counterpunch.loss_events import add_loss_flags
from counterpunch.metric import (
    find_counterpunch_opportunities,
    prepare_scorable_pitches,
    score_opportunities,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run a hitter Counterpunch breakdown.")
    parser.add_argument("--batter", type=int, required=True)
    parser.add_argument("--season", type=int, default=2024)
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def date_range_from_args(args):
    if args.start and args.end:
        return args.start, args.end
    return f"{args.season}-03-01", f"{args.season}-11-30"


def hitter_name(batter_id):
    names = playerid_reverse_lookup([batter_id], key_type="mlbam")
    if names.empty:
        return str(batter_id)
    row = names.iloc[0]
    return f"{row['name_first']} {row['name_last']}"


def print_grouped(scores, group_cols):
    print(
        scores.groupby(group_cols)
        .agg(
            opportunities=("opportunity_score", "size"),
            repeat_delta_run_exp=("repeat_delta_run_exp", "mean"),
            baseline_delta_run_exp=("baseline_delta_run_exp", "mean"),
            counterpunch_index=("opportunity_score", "mean"),
        )
        .sort_values("counterpunch_index")
        .to_string()
    )


def main():
    args = parse_args()
    start, end = date_range_from_args(args)

    df = statcast_batter(
        start_dt=start,
        end_dt=end,
        player_id=args.batter,
    ).reset_index(drop=True)
    df = add_attack_buckets(df)
    df = add_loss_flags(df)

    scorable = prepare_scorable_pitches(df)
    opportunities = find_counterpunch_opportunities(
        df, threshold=args.threshold, scorable=scorable
    )
    scores = score_opportunities(
        df,
        opportunities,
        threshold=args.threshold,
        show_progress=True,
        scorable=scorable,
    )

    name = hitter_name(args.batter)
    print(f"Hitter: {name} ({args.batter})")
    print(f"Date range: {start} to {end}")
    print(f"Location threshold: {args.threshold}")
    print(f"Opportunities: {len(scores)}")

    if scores.empty:
        return

    print("\nOverall:")
    print(
        scores[[
            "repeat_delta_run_exp",
            "baseline_delta_run_exp",
            "opportunity_score",
        ]].mean()
    )

    print("\nBy pitch group:")
    print_grouped(scores, "pitch_group")

    print("\nBy pitch group and count bucket:")
    print_grouped(scores, ["pitch_group", "count_bucket"])


if __name__ == "__main__":
    main()
