# AGENTS.md

## Work Style

Do not implement anything without user approval.
Keep changes simple and focused.
Avoid excessive helpers, tests, docs, flags, and abstractions.
Prefer the current working metric path over adding alternate modes.

## Project Overview

This repository builds a baseball analytics prototype around **Counterpunch Index**.

The metric asks how MLB hitters respond after being beaten by a pitch attack. It compares the hitter's outcome on a later similar pitch to his own baseline in a similar context.

The current priority is a clear, rerunnable season leaderboard plus simple player breakdowns.

## Current Metric Definition

Current version: **v0.2**.

A counterpunch opportunity occurs when:

1. A hitter is beaten by a pitch.
2. The hitter later sees a similar pitch in a later plate appearance.
3. The repeat pitch is scored against a hitter-specific baseline.

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
same pitch_group
same count_bucket
later plate appearance
plate_x / plate_z within 0.5 feet
```

Current baseline:

```text
hitter average delta_run_exp for same pitch_group, count_bucket, and nearby repeat location
```

The repeat pitch is excluded from its own baseline.

Current score:

```text
opportunity_score = repeat_pitch_delta_run_exp - baseline_delta_run_exp
counterpunch_index = average opportunity_score
```

## Current Repository Shape

```text
README.md
AGENTS.md
docs/metric_v0.md
src/counterpunch/
  buckets.py
  loss_events.py
  metric.py
scripts/
  download_statcast.py
  run_v0_leaderboard.py
  player_breakdown.py
  validate_leaderboard_csv.py
data/raw/
leaderboards/
```

## Module Responsibilities

### `buckets.py`

Define pitch groups and count buckets.

### `loss_events.py`

Define beaten-pitch flags.

### `metric.py`

Find counterpunch opportunities, score them, and summarize hitter scores.

## Script Responsibilities

### `download_statcast.py`

Download Statcast pitch-level data to `data/raw/`.

### `run_v0_leaderboard.py`

Run the v0.2 leaderboard from a cached CSV.

### `player_breakdown.py`

Pull one hitter directly from `pybaseball` and print a breakdown.

### `validate_leaderboard_csv.py`

Validate generated leaderboard CSVs.

## Development Guidelines

- Keep one main metric path unless the user explicitly asks for variants.
- Do not reintroduce bucket-vs-proximity mode flags unless needed.
- Do not put core logic only in notebooks.
- Do not silently drop data without reporting it.
- Do not rank hitters without showing sample size.
- Use public data sources only.
- Prefer cached raw CSVs for season leaderboards.
- Use `pybaseball.statcast_batter` for one-player breakdowns.

## Useful Commands

Download data:

```bash
python3 scripts/download_statcast.py --season 2024 --output data/raw/statcast_2024.csv
```

Run leaderboard:

```bash
python3 scripts/run_v0_leaderboard.py \
  --input-csv data/raw/statcast_2024.csv \
  --min-opportunities 100 \
  --threshold 0.5 \
  --output leaderboards/counterpunch_v0_2_2024.csv
```

Validate leaderboard:

```bash
python3 scripts/validate_leaderboard_csv.py leaderboards/counterpunch_v0_2_2024.csv
```

Run player breakdown:

```bash
python3 scripts/player_breakdown.py --batter 656976 --season 2024 --threshold 0.5
```

## Current Limitations

- The metric is exploratory.
- It is pitch-level, not plate-appearance-level.
- Runtime is not optimized.
- Pitcher identity is not currently required for repeat attacks.
- No handedness, park, pitcher, or game-context adjustment is included.
