from __future__ import annotations


class ConnectorError(RuntimeError):
    """Base error for controlled connector failures."""


class LiveFetchDisabledError(ConnectorError):
    """Raised when live fetch is requested without explicit enablement."""


class ConnectorUnavailableError(ConnectorError):
    """Raised when a connector cannot fetch from its source."""


class ConnectorRateLimitError(ConnectorError):
    """Raised when a connector would exceed its rate limit."""


class ConnectorPayloadError(ConnectorError):
    """Raised when connector input or output violates bounds."""

