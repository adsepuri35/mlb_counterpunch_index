# Counterpunch Index v0

This is the first simple definition of the metric. It is provisional and meant for exploration.

## Loss Pitch

A hitter is treated as beaten when `description` is one of:

- `called_strike`
- `swinging_strike`
- `swinging_strike_blocked`
- `foul_tip`

Fouls, foul bunts, automatic strikes, and weak contact are excluded for now.

## Similar Attack

A later pitch is considered a similar attack when it is in a later plate appearance to the same hitter and has the same:

- `pitch_group`
- `location_bucket`
- `count_bucket`

Initial bucket definitions:

- `pitch_group`
  - fastball: `FF`, `SI`, `FA`
  - cutter: `FC`
  - breaking: `SL`, `ST`, `CU`, `KC`, `SV`
  - offspeed: `CH`, `FS`
  - other: anything else
- `location_bucket`
  - heart: zones `1` through `9`
  - chase: zones `11` through `14`
  - waste: missing or anything else
- `count_bucket`
  - ahead: `strikes > balls`
  - behind: `balls > strikes`
  - even: `balls == strikes`

## Outcome Value

Use `delta_run_exp` as the pitch-level outcome value.

Higher values are treated as better for the hitter. Rows missing `delta_run_exp` are excluded from scoring.

## Opportunity Score

For each loss pitch, find the next later pitch to the same hitter with the same attack bucket in a later plate appearance.

```text
attack_bucket = pitch_group + location_bucket + count_bucket
baseline = hitter average delta_run_exp for that attack_bucket
opportunity_score = repeat_pitch_delta_run_exp - baseline
```

## Hitter Score

```text
counterpunch_index = average(opportunity_score)
opportunities = number of matched repeat attacks
```

Leaderboards must show sample size alongside the score.

## Known Limitations

- Pitch-level only, not plate-appearance-level.
- Simple location buckets based on Statcast `zone`.
- No pitcher, park, handedness, or game-context adjustment.
- Only the next similar pitch in a later plate appearance is used.
- This definition is exploratory and should not be treated as final.
