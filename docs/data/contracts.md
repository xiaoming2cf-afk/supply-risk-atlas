# Data Contracts

## Time Contract

Every time-aware record distinguishes:

- `event_time`: when the event happened.
- `ingest_time`: when the system learned it.
- `valid_from`: when a relationship starts.
- `valid_to`: when a relationship ends.
- `as_of_time`: what a prediction or snapshot is allowed to see.
- `prediction_time`: the forecast origin.

Feature computation and dataset building must enforce:

```text
feature_time <= prediction_time
ingest_time <= prediction_time
```

## Version Contract

Predictions, simulations, explanations, and reports must include:

- `graph_version`
- `feature_version`
- `label_version`
- `model_version`
- `as_of_time`
- audit or lineage reference

## Schema Evolution

Breaking schema changes require:

- ontology/config update
- Pydantic contract update
- test update
- migration or compatibility note
- owner review
