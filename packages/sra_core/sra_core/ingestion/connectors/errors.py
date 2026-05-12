from __future__ import annotations


class ConnectorError(RuntimeError):
    """Base connector failure with controlled caller-facing semantics."""


class ConnectorUnavailableError(ConnectorError):
    """Raised when live fetching is unavailable or disabled by policy."""


class ConnectorPolicyError(ConnectorError):
    """Raised when a request violates connector policy bounds."""


class ConnectorFetchError(ConnectorError):
    """Raised for bounded fetch failures."""

