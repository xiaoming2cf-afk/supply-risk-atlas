# Model Lab

The model layer consumes graph snapshots, feature values, label values, and path indexes. It must not read raw data directly.

First implementation:

- dataset builder
- temporal neighbor sampler
- baseline risk model
- DCHGT-SC skeleton
- model smoke tests

Future implementation:

- PyG HeteroData export
- Graph Transformer training loop
- causal gate
- uncertainty head
- counterfactual head
