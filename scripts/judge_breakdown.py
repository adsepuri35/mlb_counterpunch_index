import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from counterpunch.buckets import add_attack_buckets
from counterpunch.loss_events import add_loss_flags
from counterpunch.metric import find_counterpunch_opportunities, score_opportunities


JUDGE_ID = 592450


df = pd.read_csv("data/raw/statcast_2024.csv")
df = df[df["batter"] == JUDGE_ID].copy()
df = add_attack_buckets(df)
df = add_loss_flags(df)

opportunities = find_counterpunch_opportunities(
    df,
    location_mode="proximity",
    location_threshold=0.5,
)
scores = score_opportunities(
    df,
    opportunities,
    baseline_columns=["batter", "pitch_group", "count_bucket"],
)

judge = scores[scores["batter"] == JUDGE_ID].copy()

print("Aaron Judge proximity breakdown, 2024")
print(f"opportunities: {len(judge)}")
print()
print("Overall:")
print(
    judge[[
        "repeat_delta_run_exp",
        "baseline_delta_run_exp",
        "opportunity_score",
    ]].mean()
)

print("\nBy pitch group:")
print(
    judge.groupby("pitch_group")
    .agg(
        opportunities=("opportunity_score", "size"),
        repeat_delta_run_exp=("repeat_delta_run_exp", "mean"),
        baseline_delta_run_exp=("baseline_delta_run_exp", "mean"),
        counterpunch_index=("opportunity_score", "mean"),
    )
    .sort_values("counterpunch_index")
    .to_string()
)

print("\nBy pitch group and count bucket:")
print(
    judge.groupby(["pitch_group", "count_bucket"])
    .agg(
        opportunities=("opportunity_score", "size"),
        repeat_delta_run_exp=("repeat_delta_run_exp", "mean"),
        baseline_delta_run_exp=("baseline_delta_run_exp", "mean"),
        counterpunch_index=("opportunity_score", "mean"),
    )
    .sort_values("counterpunch_index")
    .to_string()
)
