from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DCHGTSCConfig:
    hidden_dim: int = 128
    heads: int = 4
    temporal_memory_dim: int = 64
    path_token_dim: int = 64
    dropout: float = 0.1


class DCHGTSCSkeleton:
    """Named module skeleton for the planned Dynamic Causal Heterogeneous Graph Transformer."""

    modules = [
        "TypeEncoder",
        "EdgeEncoder",
        "TemporalMemory",
        "RelationAttention",
        "PathTransformer",
        "CausalGate",
        "EnvironmentAdapter",
        "ShockEncoder",
        "MultiTaskHead",
        "UncertaintyHead",
        "ExplanationHead",
        "CounterfactualHead",
    ]

    def __init__(self, config: DCHGTSCConfig | None = None) -> None:
        self.config = config or DCHGTSCConfig()

    def describe(self) -> dict[str, object]:
        return {"config": self.config.__dict__, "modules": self.modules}
