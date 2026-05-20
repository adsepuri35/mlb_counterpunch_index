from pybaseball import statcast

df = statcast(start_dt="2024-04-01", end_dt="2024-04-01")
df = df.reset_index(drop=True)

key_cols = [
    "game_date",
    "game_pk",
    "batter",
    "pitcher",
    "at_bat_number",
    "pitch_number",
    "pitch_type",
    "pitch_name",
    "description",
    "events",
    "zone",
    "balls",
    "strikes",
    "plate_x",
    "plate_z",
    "delta_run_exp",
    "estimated_woba_using_speedangle",
    "launch_speed",
    "launch_angle",
]

available = [col for col in key_cols if col in df.columns]

print("Shape:")
print(df.shape)

print("\nAvailable key columns:")
print(available)

print("\nSample rows:")
print(df[available].head(20))

print("\nPitch descriptions:")
print(df["description"].value_counts(dropna=False))

print("\nPitch types:")
print(df["pitch_type"].value_counts(dropna=False))

print("\nEvents:")
print(df["events"].value_counts(dropna=False).head(30))

print("\nRun value summary:")
print(df["delta_run_exp"].describe())