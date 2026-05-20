# AGENTS.md

# Work Style

Do not implement anything on your own unless approved.
Keep everything as simple as possible. 
Avoid excessive helpers, tests, docs. etc.


## Project Overview

This repository builds a baseball analytics project around a custom metric called **Counterpunch Index**.

The goal is to measure how well MLB hitters adjust after being beaten by a specific pitch attack. Instead of only asking whether a hitter is good or bad against a pitch type overall, this project asks whether the hitter improves the next time he sees a similar pitch type, location, count context, or sequence.

The project should eventually support season-level leaderboards, hitter-specific reports, and visualizations across multiple MLB seasons.

## Core Concept

A hitter receives a counterpunch opportunity when:

1. The hitter is beaten by a pitch.
2. The hitter later sees a similar pitch attack.
3. The later outcome is compared against a baseline expectation.

The exact definition of "beaten," "similar pitch attack," and "improvement" is still evolving. Keep these definitions modular and easy to change.

## Guiding Principles

- Prefer simple, explainable metric definitions before adding complexity.
- Keep data processing, feature engineering, metric calculation, and visualization separated.
- Avoid hardcoding assumptions directly into notebooks.
- Make the project easy to rerun for different seasons.
- Make outputs interpretable for a baseball analytics audience.
- Prioritize correctness and clarity over premature optimization.
- Use public data sources only unless explicitly instructed otherwise.

## Expected Data Sources

The main intended data source is pitch-level Statcast data.

Likely fields include:

- game date
- game ID
- batter ID
- pitcher ID
- pitch type
- pitch location
- count
- pitch result
- plate appearance result
- batted-ball outcome
- estimated wOBA or run value fields when available
- exit velocity
- launch angle

Do not assume every field is always present. Code should handle missing optional columns gracefully.

## Repository Structure

Use this general structure unless the existing repo evolves differently:

```text
counterpunch-index/
  README.md
  AGENTS.md
  pyproject.toml or requirements.txt
  data/
    raw/
    interim/
    processed/
  notebooks/
  src/
    counterpunch/
      data.py
      features.py
      buckets.py
      loss_events.py
      metric.py
      leaderboards.py
      plots.py
  scripts/
  leaderboards/
  reports/
````

## Module Responsibilities

### `data.py`

Handle data loading, saving, caching, and basic validation.

### `features.py`

Create derived pitch-level and plate-appearance-level features.

### `buckets.py`

Define pitch type groups, location buckets, count buckets, and other grouping logic.

### `loss_events.py`

Define whether a hitter was beaten by a pitch.

### `metric.py`

Calculate Counterpunch Index and related variants.

### `leaderboards.py`

Aggregate player-season results and create ranked outputs.

### `plots.py`

Generate visualizations for reports and notebooks.

## Metric Design Expectations

Keep the metric logic modular.

Avoid writing one giant function that does all of the following at once:

* load data
* clean data
* define losses
* find repeat attacks
* calculate baselines
* rank hitters
* plot results

Instead, break the logic into small functions with clear inputs and outputs.

Example conceptual flow:

```text
load pitch-level data
clean and validate data
create pitch/location/count buckets
identify loss events
find later similar pitch attacks
calculate baseline hitter performance
calculate post-loss performance
compute Counterpunch Index
generate leaderboards
```

## Coding Style

* Use Python.
* Prefer pandas for tabular processing unless another library is clearly better.
* Use clear function names.
* Use type hints where helpful.
* Keep functions small and testable.
* Avoid overly clever code.
* Add comments only where they clarify non-obvious logic.
* Prefer explicit column names and documented assumptions.

## Notebooks

Notebooks should be used for exploration, validation, and visualization.

Do not put core project logic only in notebooks. If a notebook contains reusable logic, move it into `src/counterpunch/`.

Good notebook goals:

* inspect raw Statcast data
* test early metric definitions
* validate sample players
* generate exploratory leaderboards
* create visual examples of counterpunch opportunities

## Testing and Validation

When adding or changing metric logic, include simple tests where practical.

Useful tests include:

* pitch buckets are assigned correctly
* loss events are detected correctly
* repeat attacks are found in chronological order
* baselines exclude the target repeat event when needed
* leaderboard aggregation handles low-sample players correctly
* missing optional columns do not break the pipeline

Use small synthetic datasets for unit tests when possible.

## Data Handling

* Do not commit large raw data files unless explicitly intended.
* Store generated leaderboards and small processed outputs when useful.
* Keep raw, interim, and processed data separate.
* Make scripts rerunnable.
* Prefer deterministic outputs.

## Output Expectations

The project should eventually produce:

* season-level hitter leaderboards
* multi-season hitter leaderboards
* player-specific breakdowns
* summary charts
* example counterpunch sequences
* a clear README explaining the metric

## README Expectations

The README should explain:

* what Counterpunch Index measures
* why it is different from standard pitch-type splits
* how the metric is calculated at a high level
* how to run the pipeline
* how to interpret the leaderboard
* current limitations

## Important Constraints

* Do not overfit the first version of the metric.
* Do not make the metric too complex before a simple version works.
* Do not assume the first formula is final.
* Do not silently drop large amounts of data without reporting it.
* Do not rank players without showing sample size.
* Do not present exploratory results as definitive.

## Development Workflow

When implementing new functionality:

1. Identify the relevant module.
2. Add or update small reusable functions.
3. Add lightweight validation or tests if practical.
4. Update notebooks only after reusable code exists.
5. Keep outputs reproducible.
6. Document assumptions if they affect the metric.

## Current Project Stage

This project is in the early design/prototyping stage.

Favor flexible architecture over final polish. The goal is to create a clean foundation that can support multiple definitions of Counterpunch Index as the metric evolves.