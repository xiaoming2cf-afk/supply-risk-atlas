# API Envelope

All API responses return:

```json
{
  "request_id": "req_123",
  "status": "success",
  "data": {},
  "metadata": {
    "graph_version": "g_20260201",
    "feature_version": "f_20260201",
    "label_version": "l_20260201",
    "model_version": "baseline_v0.1.0",
    "as_of_time": "2026-02-01T00:00:00Z"
  },
  "warnings": [],
  "errors": []
}
```

OpenAPI is the interface source of truth. Frontend code must consume the shared API client rather than scattering raw `fetch` calls.
