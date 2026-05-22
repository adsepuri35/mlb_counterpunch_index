# MLB Counterpunch Index

Counterpunch Index is a prototype baseball metric for measuring how hitters respond after being beaten by a pitch attack.

Instead of asking only whether a hitter is good against a pitch type overall, this project asks:

```text
After a hitter is beaten, what happens the next time he sees a similar pitch attack?
```

## Current Metric: v0.2

A hitter gets a counterpunch opportunity when:

1. He is beaten by a pitch.
2. In a later plate appearance, he sees a similar pitch attack.
3. The repeat pitch outcome is compared to his own baseline in a similar context.

Current loss pitch descriptions:

```text
called_strike
swinging_strike
swinging_strike_blocked
foul_tip
```

Current similar attack definition:

```text
same hitter
same pitch group
same count bucket
later plate appearance
pitch location within 0.5 feet using plate_x / plate_z
```

Current score:

```text
baseline = hitter average delta_run_exp for same pitch group, count bucket, and nearby repeat location
opportunity_score = repeat_pitch_delta_run_exp - baseline
counterpunch_index = average opportunity_score
```

The repeat pitch is excluded from its own baseline.

## Data

The project uses public Statcast pitch-level data from `pybaseball`.

Download a season once:

```bash
python3 scripts/download_statcast.py \
  --season 2024 \
  --output data/raw/statcast_2024.csv
```

Large raw data files should stay local and are ignored by git.

## Run Leaderboard

```bash
python3 scripts/run_v0_leaderboard.py \
  --input-csv data/raw/statcast_2024.csv \
  --min-opportunities 100 \
  --threshold 0.5 \
  --output leaderboards/counterpunch_v0_2_2024.csv
```

Output columns include:

```text
rank
batter
hitter_name
opportunities
counterpunch_index
repeat_delta_run_exp
baseline_delta_run_exp
avg_baseline_sample_size
```

Always interpret rankings with sample size.

## Validate Leaderboard

```bash
python3 scripts/validate_leaderboard_csv.py \
  leaderboards/counterpunch_v0_2_2024.csv
```

This checks required columns, missing values, rank order, minimum opportunities, and score arithmetic.

## Player Breakdown

Run a hitter-specific breakdown directly from `pybaseball`:

```bash
python3 scripts/player_breakdown.py \
  --batter 656976 \
  --season 2024 \
  --threshold 0.5
```

The script prints overall results plus breakdowns by pitch group and count bucket.

## Current Limitations

- This is exploratory, not a finished metric.
- Pitch-level outcome uses `delta_run_exp`.
- Similarity uses a fixed location threshold.
- Count context is simplified to ahead, behind, and even.
- Pitcher identity, handedness, park, and game context are not adjusted.
- Runtime can be slow on full-season data because baselines are location-aware.
