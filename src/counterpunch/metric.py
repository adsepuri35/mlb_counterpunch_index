"""Counterpunch Index v0.2 matching and scoring."""

import pandas as pd


def prepare_scorable_pitches(df):
    sort_cols = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    return (
        df.dropna(subset=["delta_run_exp", "plate_x", "plate_z"])
        .sort_values(sort_cols)
        .reset_index(drop=True)
    )


def find_counterpunch_opportunities(df, threshold=0.5, scorable=None):
    if scorable is None:
        scorable = prepare_scorable_pitches(df)
    opportunities = []
    threshold_sq = threshold * threshold

    group_cols = ["batter", "pitch_group", "count_bucket"]
    for _, group in scorable.groupby(group_cols, sort=False):
        indexes = group.index.to_numpy()
        at_bats = group["at_bat_number"].to_numpy()
        plate_x = group["plate_x"].to_numpy()
        plate_z = group["plate_z"].to_numpy()
        is_loss = group["is_loss"].to_numpy()

        for i in range(len(group) - 1):
            if not is_loss[i]:
                continue

            for j in range(i + 1, len(group)):
                if at_bats[j] <= at_bats[i]:
                    continue
                if not is_near_location(
                    plate_x[i], plate_z[i], plate_x[j], plate_z[j], threshold_sq
                ):
                    continue

                opportunities.append((indexes[i], indexes[j]))
                break

    return opportunities


def is_near_location(loss_x, loss_z, repeat_x, repeat_z, threshold_sq):
    x_diff = repeat_x - loss_x
    z_diff = repeat_z - loss_z
    return x_diff * x_diff + z_diff * z_diff <= threshold_sq


def build_baseline_groups(scorable):
    groups = {}
    group_cols = ["batter", "pitch_group", "count_bucket"]
    for key, group in scorable.groupby(group_cols, sort=False):
        groups[key] = {
            "plate_x": group["plate_x"].to_numpy(),
            "plate_z": group["plate_z"].to_numpy(),
            "delta_run_exp": group["delta_run_exp"].to_numpy(),
        }
    return groups


def score_opportunities(
    df,
    opportunities,
    threshold=0.5,
    show_progress=False,
    progress_every=1000,
    scorable=None,
):
    if not opportunities:
        return pd.DataFrame()

    if scorable is None:
        scorable = prepare_scorable_pitches(df)
    baseline_groups = build_baseline_groups(scorable)
    scored = []
    total = len(opportunities)
    threshold_sq = threshold * threshold

    for i, (loss_idx, repeat_idx) in enumerate(opportunities, start=1):
        if show_progress and (i == 1 or i % progress_every == 0 or i == total):
            print(f"Scoring opportunities: {i}/{total}", flush=True)

        loss_pitch = scorable.iloc[loss_idx]
        repeat_pitch = scorable.iloc[repeat_idx]
        key = (
            repeat_pitch["batter"],
            repeat_pitch["pitch_group"],
            repeat_pitch["count_bucket"],
        )
        baseline_group = baseline_groups[key]
        near_location = (
            (baseline_group["plate_x"] - repeat_pitch["plate_x"]) ** 2
            + (baseline_group["plate_z"] - repeat_pitch["plate_z"]) ** 2
            <= threshold_sq
        )

        baseline_sum = (
            baseline_group["delta_run_exp"][near_location].sum()
            - repeat_pitch["delta_run_exp"]
        )
        baseline_count = near_location.sum() - 1
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
                "baseline_sample_size": baseline_count,
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
            avg_baseline_sample_size=("baseline_sample_size", "mean"),
            counterpunch_index=("opportunity_score", "mean"),
        )
        .reset_index()
    )
