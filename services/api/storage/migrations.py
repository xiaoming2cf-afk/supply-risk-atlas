from __future__ import annotations

from pathlib import Path

from services.api.storage.sqlite_store import SQLiteStore


def initialize_storage(path: str | Path | None = None) -> SQLiteStore:
    store = SQLiteStore(path)
    store.initialize()
    return store
