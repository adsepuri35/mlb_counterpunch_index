import sys
from pathlib import Path

from pybaseball import statcast

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from counterpunch.buckets import add_attack_buckets
from counterpunch.loss_events import add_loss_flags
from counterpunch.metric import (
    find_counterpunch_opportunities,
    prepare_scorable_pitches,
    score_opportunities,
    summarize_hitter_scores,
)


df = statcast(start_dt="2024-04-01", end_dt="2024-04-07")
df = df.reset_index(drop=True)

df = add_attack_buckets(df)
df = add_loss_flags(df)

scorable = prepare_scorable_pitches(df)
pa_bucket_counts = scorable.groupby(["batter", "attack_bucket"])[
    "at_bat_number"
].nunique()
repeat_buckets = pa_bucket_counts[pa_bucket_counts >= 2]
losses = scorable[scorable["is_loss"]]
opportunities = find_counterpunch_opportunities(df)
scores = score_opportunities(df, opportunities)
hitter_scores = summarize_hitter_scores(scores)

print("Rows:")
print(len(df))

print("\nRows with delta_run_exp:")
print(len(scorable))

print("\nLoss pitches:")
print(len(losses))

print("\nPitch groups:")
print(df["pitch_group"].value_counts(dropna=False))

print("\nLocation buckets:")
print(df["location_bucket"].value_counts(dropna=False))

print("\nCount buckets:")
print(df["count_bucket"].value_counts(dropna=False))

print("\nHitter attack buckets with repeats across PAs:")
print(len(repeat_buckets))

print("\nMatched opportunities:")
print(len(opportunities))


if not scores.empty:
    print("\nScore summary:")
    print(
        scores[[
            "repeat_delta_run_exp",
            "baseline_delta_run_exp",
            "opportunity_score",
        ]].mean()
    )

    print("\nTop hitters by Counterpunch Index:")
    print(
        hitter_scores.sort_values("counterpunch_index", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print("\nBottom hitters by Counterpunch Index:")
    print(
        hitter_scores.sort_values("counterpunch_index", ascending=True)
        .head(10)
        .to_string(index=False)
    )

    qualified = hitter_scores[hitter_scores["opportunities"] >= 10]
    print("\nHitters with 10+ opportunities:")
    print(len(qualified))

    if not qualified.empty:
        print("\nTop qualified hitters by Counterpunch Index:")
        print(
            qualified.sort_values("counterpunch_index", ascending=False)
            .head(10)
            .to_string(index=False)
        )

        print("\nBottom qualified hitters by Counterpunch Index:")
        print(
            qualified.sort_values("counterpunch_index", ascending=True)
            .head(10)
            .to_string(index=False)
        )

print("\nExample matched opportunities:")
example_cols = [
    "batter",
    "game_pk",
    "at_bat_number",
    "pitch_number",
    "pitch_type",
    "description",
    "zone",
    "balls",
    "strikes",
    "attack_bucket",
    "delta_run_exp",
]
for n, (loss_pitch, repeat_pitch) in enumerate(opportunities[:10], start=1):
    print(f"\nExample {n}")
    print("loss:")
    print(loss_pitch[example_cols].to_string())
    print("repeat:")
    print(repeat_pitch[example_cols].to_string())
