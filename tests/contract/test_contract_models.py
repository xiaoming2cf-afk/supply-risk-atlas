from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sra_core.contracts.domain import ApiEnvelope, EdgeState, VersionMetadata
from sra_core.quality import validate_api_envelope


def test_api_envelope_requires_version_metadata() -> None:
    metadata = VersionMetadata(
        graph_version="g_test",
        feature_version="f_test",
        label_version="l_test",
        model_version="m_test",
        as_of_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    envelope = ApiEnvelope(
        request_id="req_test",
        status="success",
        data={"ok": True},
        metadata=metadata,
        warnings=[],
        errors=[],
    )
    assert validate_api_envelope(envelope) == []


def test_edge_state_rejects_invalid_interval() -> None:
    with pytest.raises(ValidationError):
        EdgeState(
            edge_id="edge_bad",
            source_id="firm_a",
            target_id="firm_b",
            edge_type="supplies_to",
            valid_from=datetime(2026, 2, 1, tzinfo=timezone.utc),
            valid_to=datetime(2026, 1, 1, tzinfo=timezone.utc),
            confidence=0.9,
            graph_version="g_test",
            source="unit",
        )
