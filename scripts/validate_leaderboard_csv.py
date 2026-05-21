import argparse

import pandas as pd


REQUIRED_COLUMNS = [
    "rank",
    "date_start",
    "date_end",
    "min_opportunities",
    "batter",
    "hitter_name",
    "opportunities",
    "counterpunch_index",
    "repeat_delta_run_exp",
    "baseline_delta_run_exp",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Validate a Counterpunch v0 leaderboard CSV.")
    parser.add_argument("csv_path")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    return parser.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.csv_path)
    warnings = []

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise SystemExit(f"Missing required columns: {missing_columns}")

    if df.empty:
        raise SystemExit("CSV has no rows.")

    expected_rank = pd.Series(range(1, len(df) + 1), index=df.index)
    if not df["rank"].equals(expected_rank):
        warnings.append("rank is not sequential from 1")

    if not df["counterpunch_index"].is_monotonic_decreasing:
        warnings.append("counterpunch_index is not sorted descending")

    min_opportunities = df["min_opportunities"].iloc[0]
    if not (df["min_opportunities"] == min_opportunities).all():
        warnings.append("min_opportunities is not constant")

    location_mode = None
    location_threshold = None
    if "location_mode" in df.columns:
        location_mode = df["location_mode"].iloc[0]
        if not (df["location_mode"] == location_mode).all():
            warnings.append("location_mode is not constant")
    if "location_threshold" in df.columns:
        location_threshold = df["location_threshold"].iloc[0]
        if not (df["location_threshold"] == location_threshold).all():
            warnings.append("location_threshold is not constant")

    below_min = df[df["opportunities"] < df["min_opportunities"]]
    if not below_min.empty:
        warnings.append(f"{len(below_min)} rows are below min_opportunities")

    expected_score = df["repeat_delta_run_exp"] - df["baseline_delta_run_exp"]
    max_score_error = (df["counterpunch_index"] - expected_score).abs().max()
    if max_score_error > args.tolerance:
        warnings.append(f"max score arithmetic error is {max_score_error}")

    missing_names = df["hitter_name"].isna().sum()
    blank_names = (df["hitter_name"].fillna("").str.strip() == "").sum()
    if missing_names or blank_names:
        warnings.append(f"missing or blank hitter names: {missing_names + blank_names}")

    print(f"File: {args.csv_path}")
    print(f"Rows: {len(df)}")
    print(f"Date range: {df['date_start'].iloc[0]} to {df['date_end'].iloc[0]}")
    print(f"Min opportunities: {min_opportunities}")
    if location_mode is not None:
        print(f"Location mode: {location_mode}")
    if location_threshold is not None:
        print(f"Location threshold: {location_threshold}")

    print("\nMissing values:")
    summary_columns = REQUIRED_COLUMNS + [
        col for col in ["location_mode", "location_threshold"] if col in df.columns
    ]
    print(df[summary_columns].isna().sum())

    print("\nOpportunities summary:")
    print(df["opportunities"].describe())

    print("\nCounterpunch Index summary:")
    print(df["counterpunch_index"].describe())

    print("\nScore arithmetic:")
    print(f"max abs error: {max_score_error}")

    print("\nTop rows:")
    print(df.head(args.limit).to_string(index=False))

    print("\nBottom rows:")
    print(df.tail(args.limit).to_string(index=False))

    print("\nWarnings:")
    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("None")


if __name__ == "__main__":
    main()
