# Temporal Heterogeneous Graph Kernel

The graph kernel stores events first and materializes state second.

## Edge Event

`edge_event` is append-only. It records creates, updates, decays, and removals with source, confidence, event time, and ingest time.

## Edge State

`edge_state` is derived from visible edge events. It is used for graph snapshots, path indexing, features, simulation, and API responses.

## Snapshot Determinism

For identical entities, edge events, configuration, and `as_of_time`, snapshot checksum must be stable.

## Counterfactual Isolation

Counterfactual graphs are copied from base states and assigned a new graph version. They must not mutate the base graph.
