from pybaseball import statcast


LOSS_DESCRIPTIONS = {
    "called_strike",
    "swinging_strike",
    "swinging_strike_blocked",
    "foul_tip",
}


def pitch_group(pitch_type):
    if pitch_type in {"FF", "SI", "FA"}:
        return "fastball"
    if pitch_type == "FC":
        return "cutter"
    if pitch_type in {"SL", "ST", "CU", "KC", "SV"}:
        return "breaking"
    if pitch_type in {"CH", "FS"}:
        return "offspeed"
    return "other"


def location_bucket(zone):
    if zone in range(1, 10):
        return "heart"
    if zone in range(11, 15):
        return "chase"
    return "waste"


def count_bucket(row):
    if row["strikes"] > row["balls"]:
        return "ahead"
    if row["balls"] > row["strikes"]:
        return "behind"
    return "even"


df = statcast(start_dt="2024-04-01", end_dt="2024-04-01")
df = df.reset_index(drop=True)

df["pitch_group"] = df["pitch_type"].apply(pitch_group)
df["location_bucket"] = df["zone"].apply(location_bucket)
df["count_bucket"] = df.apply(count_bucket, axis=1)
df["attack_bucket"] = (
    df["pitch_group"] + "|" + df["location_bucket"] + "|" + df["count_bucket"]
)
df["is_loss"] = df["description"].isin(LOSS_DESCRIPTIONS)

scorable = df.dropna(subset=["delta_run_exp"])
pa_bucket_counts = scorable.groupby(["batter", "attack_bucket"])["at_bat_number"].nunique()
repeat_buckets = pa_bucket_counts[pa_bucket_counts >= 2]

losses = scorable[scorable["is_loss"]]

sort_cols = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
scorable = scorable.sort_values(sort_cols).reset_index(drop=True)

opportunities = []
for _, group in scorable.groupby(["batter", "attack_bucket"], sort=False):
    rows = list(group.iterrows())
    for i, (_, loss_pitch) in enumerate(rows[:-1]):
        if loss_pitch["is_loss"]:
            later_pitches = [
                row
                for _, row in rows[i + 1 :]
                if row["at_bat_number"] > loss_pitch["at_bat_number"]
            ]
            if later_pitches:
                opportunities.append((loss_pitch, later_pitches[0]))


baselines = scorable.groupby(["batter", "attack_bucket"])["delta_run_exp"].mean()
scored_opportunities = []
for loss_pitch, repeat_pitch in opportunities:
    key = (repeat_pitch["batter"], repeat_pitch["attack_bucket"])
    baseline = baselines.loc[key]
    repeat_outcome = repeat_pitch["delta_run_exp"]
    scored_opportunities.append(
        {
            "batter": repeat_pitch["batter"],
            "attack_bucket": repeat_pitch["attack_bucket"],
            "loss_delta_run_exp": loss_pitch["delta_run_exp"],
            "repeat_delta_run_exp": repeat_outcome,
            "baseline_delta_run_exp": baseline,
            "opportunity_score": repeat_outcome - baseline,
        }
    )

scores = df.iloc[0:0].copy()
if scored_opportunities:
    import pandas as pd

    scores = pd.DataFrame(scored_opportunities)

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
    print(scores[["repeat_delta_run_exp", "baseline_delta_run_exp", "opportunity_score"]].mean())

    hitter_scores = (
        scores.groupby("batter")
        .agg(
            opportunities=("opportunity_score", "size"),
            repeat_delta_run_exp=("repeat_delta_run_exp", "mean"),
            baseline_delta_run_exp=("baseline_delta_run_exp", "mean"),
            counterpunch_index=("opportunity_score", "mean"),
        )
        .reset_index()
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
