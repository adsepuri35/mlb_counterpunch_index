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
    df["pitch_group"] = df["pitch_type"].apply(assign_pitch_group)
    df["location_bucket"] = df["zone"].apply(assign_location_bucket)
    df["count_bucket"] = df.apply(assign_count_bucket, axis=1)
    df["attack_bucket"] = (
        df["pitch_group"] + "|" + df["location_bucket"] + "|" + df["count_bucket"]
    )
    return df
