"""Counterpunch Index v0 matching and scoring."""

import pandas as pd


def prepare_scorable_pitches(df):
    sort_cols = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    return (
        df.dropna(subset=["delta_run_exp"])
        .sort_values(sort_cols)
        .reset_index(drop=True)
    )


def find_counterpunch_opportunities(df):
    scorable = prepare_scorable_pitches(df)
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

    return opportunities


def score_opportunities(df, opportunities):
    if not opportunities:
        return pd.DataFrame()

    scorable = prepare_scorable_pitches(df)
    baselines = scorable.groupby(["batter", "attack_bucket"])["delta_run_exp"].mean()

    scored = []
    for loss_pitch, repeat_pitch in opportunities:
        key = (repeat_pitch["batter"], repeat_pitch["attack_bucket"])
        baseline = baselines.loc[key]
        repeat_outcome = repeat_pitch["delta_run_exp"]
        scored.append(
            {
                "batter": repeat_pitch["batter"],
                "attack_bucket": repeat_pitch["attack_bucket"],
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
