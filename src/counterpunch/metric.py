"""Counterpunch Index v0.2 matching and scoring."""

import pandas as pd


def prepare_scorable_pitches(df):
    sort_cols = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    return (
        df.dropna(subset=["delta_run_exp", "plate_x", "plate_z"])
        .sort_values(sort_cols)
        .reset_index(drop=True)
    )


def find_counterpunch_opportunities(df, threshold=0.5):
    scorable = prepare_scorable_pitches(df)
    opportunities = []

    group_cols = ["batter", "pitch_group", "count_bucket"]
    for _, group in scorable.groupby(group_cols, sort=False):
        rows = list(group.iterrows())
        for i, (_, loss_pitch) in enumerate(rows[:-1]):
            if not loss_pitch["is_loss"]:
                continue

            for _, repeat_pitch in rows[i + 1 :]:
                if repeat_pitch["at_bat_number"] <= loss_pitch["at_bat_number"]:
                    continue
                if not is_near_location(loss_pitch, repeat_pitch, threshold):
                    continue

                opportunities.append((loss_pitch, repeat_pitch))
                break

    return opportunities


def is_near_location(loss_pitch, repeat_pitch, threshold):
    x_diff = repeat_pitch["plate_x"] - loss_pitch["plate_x"]
    z_diff = repeat_pitch["plate_z"] - loss_pitch["plate_z"]
    return (x_diff * x_diff + z_diff * z_diff) ** 0.5 <= threshold


def score_opportunities(
    df,
    opportunities,
    threshold=0.5,
    show_progress=False,
    progress_every=1000,
):
    if not opportunities:
        return pd.DataFrame()

    scorable = prepare_scorable_pitches(df)
    scored = []
    total = len(opportunities)

    for i, (loss_pitch, repeat_pitch) in enumerate(opportunities, start=1):
        if show_progress and (i == 1 or i % progress_every == 0 or i == total):
            print(f"Scoring opportunities: {i}/{total}", flush=True)

        baseline_rows = scorable[
            (scorable["batter"] == repeat_pitch["batter"])
            & (scorable["pitch_group"] == repeat_pitch["pitch_group"])
            & (scorable["count_bucket"] == repeat_pitch["count_bucket"])
        ]
        baseline_rows = baseline_rows[
            ((baseline_rows["plate_x"] - repeat_pitch["plate_x"]) ** 2
            + (baseline_rows["plate_z"] - repeat_pitch["plate_z"]) ** 2)
            ** 0.5
            <= threshold
        ]

        baseline_sum = baseline_rows["delta_run_exp"].sum() - repeat_pitch["delta_run_exp"]
        baseline_count = len(baseline_rows) - 1
        if baseline_count <= 0:
            continue

        baseline = baseline_sum / baseline_count
        repeat_outcome = repeat_pitch["delta_run_exp"]
        scored.append(
            {
                "batter": repeat_pitch["batter"],
                "pitch_group": repeat_pitch["pitch_group"],
                "count_bucket": repeat_pitch["count_bucket"],
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
