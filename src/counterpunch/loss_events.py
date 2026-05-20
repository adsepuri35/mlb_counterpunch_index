"""Loss pitch definitions for Counterpunch Index v0."""

LOSS_DESCRIPTIONS = {
    "called_strike",
    "swinging_strike",
    "swinging_strike_blocked",
    "foul_tip",
}


def add_loss_flags(df):
    df = df.copy()
    df["is_loss"] = df["description"].isin(LOSS_DESCRIPTIONS)
    return df
