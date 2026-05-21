"""Counterpunch Index v0 matching and scoring."""

import pandas as pd


def prepare_scorable_pitches(df):
    sort_cols = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    return (
        df.dropna(subset=["delta_run_exp"])
        .sort_values(sort_cols)
        .reset_index(drop=True)
    )


def find_counterpunch_opportunities(
    df,
    location_mode="bucket",
    location_threshold=0.5,
):
    scorable = prepare_scorable_pitches(df)
    opportunities = []

    if location_mode == "bucket":
        group_cols = ["batter", "attack_bucket"]
    elif location_mode == "proximity":
        group_cols = ["batter", "pitch_group", "count_bucket"]
        scorable = scorable.dropna(subset=["plate_x", "plate_z"])
    else:
        raise ValueError(f"Unknown location_mode: {location_mode}")

    for _, group in scorable.groupby(group_cols, sort=False):
        rows = list(group.iterrows())
        for i, (_, loss_pitch) in enumerate(rows[:-1]):
            if not loss_pitch["is_loss"]:
                continue

            for _, repeat_pitch in rows[i + 1 :]:
                if repeat_pitch["at_bat_number"] <= loss_pitch["at_bat_number"]:
                    continue
                if location_mode == "proximity" and not is_near_location(
                    loss_pitch, repeat_pitch, location_threshold
                ):
                    continue

                opportunities.append((loss_pitch, repeat_pitch))
                break

    return opportunities


def is_near_location(loss_pitch, repeat_pitch, threshold):
    x_diff = repeat_pitch["plate_x"] - loss_pitch["plate_x"]
    z_diff = repeat_pitch["plate_z"] - loss_pitch["plate_z"]
    return (x_diff * x_diff + z_diff * z_diff) ** 0.5 <= threshold


def score_opportunities(df, opportunities, baseline_columns=None):
    if not opportunities:
        return pd.DataFrame()

    if baseline_columns is None:
        baseline_columns = ["batter", "attack_bucket"]

    scorable = prepare_scorable_pitches(df)
    baseline_parts = scorable.groupby(baseline_columns)["delta_run_exp"].agg(
        ["sum", "count"]
    )

    scored = []
    for loss_pitch, repeat_pitch in opportunities:
        key = tuple(repeat_pitch[col] for col in baseline_columns)
        if len(key) == 1:
            key = key[0]
        baseline_sum = baseline_parts.loc[key, "sum"] - repeat_pitch["delta_run_exp"]
        baseline_count = baseline_parts.loc[key, "count"] - 1
        if baseline_count <= 0:
            continue

        baseline = baseline_sum / baseline_count
        repeat_outcome = repeat_pitch["delta_run_exp"]
        scored.append(
            {
                "batter": repeat_pitch["batter"],
                "attack_bucket": repeat_pitch["attack_bucket"],
                "pitch_group": repeat_pitch.get("pitch_group"),
                "count_bucket": repeat_pitch.get("count_bucket"),
                "loss_delta_run_exp": loss_pitch["delta_run_exp"],
                "repeat_delta_run_exp": repeat_outcome,
                "baseline_delta_run_exp": baseline,
                "opportunity_score": repeat_outcome - baseline,
            }
        )

    return pd.DataFrame(scored)


def summarize_hitter_scores(scores):
    if scores.empty:
        return pd.DataFrame()

    return (
        scores.groupby("batter")
        .agg(
            opportunities=("opportunity_score", "size"),
            repeat_delta_run_exp=("repeat_delta_run_exp", "mean"),
            baseline_delta_run_exp=("baseline_delta_run_exp", "mean"),
            counterpunch_index=("opportunity_score", "mean"),
        )
        .reset_index()
    )
