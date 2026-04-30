from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Environment:
    environment_id: str
    environment_type: str
    name: str
    filter_rule: str
    start_time: datetime
    end_time: datetime


@dataclass
class EnvironmentRegistry:
    environments: dict[str, Environment]

    def register(self, environment: Environment) -> None:
        self.environments[environment.environment_id] = environment


@dataclass(frozen=True)
class Intervention:
    intervention_id: str
    intervention_type: str
    target_id: str
    parameters: dict[str, Any]
    created_by: str
    created_at: datetime


@dataclass
class InterventionRegistry:
    interventions: dict[str, Intervention]

    def register(self, intervention: Intervention) -> None:
        self.interventions[intervention.intervention_id] = intervention
