# Counterpunch Index v0.2

This is the current prototype definition. It uses pitch-location proximity instead of broad location buckets.

## Loss Pitch

A hitter is treated as beaten when `description` is one of:

- `called_strike`
- `swinging_strike`
- `swinging_strike_blocked`
- `foul_tip`

## Similar Attack

A later pitch is considered a similar attack when it is in a later plate appearance to the same hitter and has the same:

- `pitch_group`
- `count_bucket`

The repeat pitch must also be near the loss pitch location using Statcast `plate_x` and `plate_z`. The current threshold is `0.5` feet. The optional same-pitcher analysis path also requires the loss pitch and repeat pitch to have the same `pitcher`; the baseline remains hitter-specific.

## Buckets

Pitch groups:

- fastball: `FF`, `SI`, `FA`
- cutter: `FC`
- breaking: `SL`, `ST`, `CU`, `KC`, `SV`
- offspeed: `CH`, `FS`
- other: anything else

Count buckets, from the hitter perspective:

- ahead: `balls > strikes`
- behind: `strikes > balls`
- even: `balls == strikes`

## Outcome Value

Use `delta_run_exp` as the pitch-level outcome value. Higher values are treated as better for the hitter.

## Baseline and Score

For each matched repeat pitch:

```text
baseline = hitter average delta_run_exp for same pitch_group + count_bucket + nearby repeat location
baseline_sample_size = count of nearby baseline pitches, excluding the repeat pitch
opportunity_score = repeat_pitch_delta_run_exp - baseline
```

Opportunities can optionally be filtered with `min_baseline_sample_size` so thin individual baselines are not scored.

The repeat pitch is excluded from its own baseline.

## Hitter Score

```text
counterpunch_index = average(opportunity_score)
opportunities = number of matched repeat attacks
avg_baseline_sample_size = average baseline_sample_size across scored opportunities
support_tier = thin if avg_baseline_sample_size < 15, medium if < 30, otherwise strong
```

Leaderboards must show sample size alongside the score.

## Known Limitations

- Pitch-level only, not plate-appearance-level.
- No pitcher, park, handedness, or game-context adjustment.
- Uses a fixed location threshold.
- This definition is exploratory and should not be treated as final.
