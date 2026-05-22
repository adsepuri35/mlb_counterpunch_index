"""Bucket definitions for Counterpunch Index v0."""


def assign_pitch_group(pitch_type):
    if pitch_type in {"FF", "SI", "FA"}:
        return "fastball"
    if pitch_type == "FC":
        return "cutter"
    if pitch_type in {"SL", "ST", "CU", "KC", "SV"}:
        return "breaking"
    if pitch_type in {"CH", "FS"}:
        return "offspeed"
    return "other"


def assign_location_bucket(zone):
    if zone in range(1, 10):
        return "heart"
    if zone in range(11, 15):
        return "chase"
    return "waste"


def assign_count_bucket(row):
    if row["strikes"] > row["balls"]:
        return "ahead"
    if row["balls"] > row["strikes"]:
        return "behind"
    return "even"


def add_attack_buckets(df):
    df = df.copy()

    df["pitch_group"] = "other"
    df.loc[df["pitch_type"].isin({"FF", "SI", "FA"}), "pitch_group"] = "fastball"
    df.loc[df["pitch_type"] == "FC", "pitch_group"] = "cutter"
    df.loc[
        df["pitch_type"].isin({"SL", "ST", "CU", "KC", "SV"}), "pitch_group"
    ] = "breaking"
    df.loc[df["pitch_type"].isin({"CH", "FS"}), "pitch_group"] = "offspeed"

    df["location_bucket"] = "waste"
    df.loc[df["zone"].isin(range(1, 10)), "location_bucket"] = "heart"
    df.loc[df["zone"].isin(range(11, 15)), "location_bucket"] = "chase"

    df["count_bucket"] = "even"
    df.loc[df["strikes"] > df["balls"], "count_bucket"] = "ahead"
    df.loc[df["balls"] > df["strikes"], "count_bucket"] = "behind"

    df["attack_bucket"] = (
        df["pitch_group"] + "|" + df["location_bucket"] + "|" + df["count_bucket"]
    )
    return df
