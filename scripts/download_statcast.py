import argparse
from pathlib import Path

from pybaseball import statcast


def parse_args():
    parser = argparse.ArgumentParser(description="Download Statcast pitch data to CSV.")
    parser.add_argument("--season", type=int, default=2024)
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--output")
    return parser.parse_args()


def date_range_from_args(args):
    if args.start and args.end:
        return args.start, args.end
    return f"{args.season}-03-01", f"{args.season}-11-30"


def main():
    args = parse_args()
    start, end = date_range_from_args(args)
    output = args.output or f"data/raw/statcast_{args.season}.csv"

    df = statcast(start_dt=start, end_dt=end).reset_index(drop=True)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Date range: {start} to {end}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
