"""In-memory robot state shared by all routes of one emulator app instance.

Mutations only happen inside async handlers between awaits (single event
loop), but a lock is still taken so the store stays correct if handlers are
ever executed from worker threads.
"""

from __future__ import annotations

import threading
from typing import Any


class StateStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.collections: dict[str, dict[str, dict]] = {}
        self.seeded: set[str] = set()
        self.singletons: dict[str, dict] = {}
        self._guid_counter = 0
        self._int_counter = 0

    def next_guid(self) -> str:
        with self._lock:
            self._guid_counter += 1
            return f"emulated-0000-0000-{self._guid_counter:04x}-000000000000"

    def next_int_id(self) -> int:
        with self._lock:
            self._int_counter += 1
            return self._int_counter

    def collection(self, key: str) -> dict[str, dict]:
        with self._lock:
            return self.collections.setdefault(key, {})

    def seed_once(self, key: str, items: list[tuple[str, dict]]) -> None:
        with self._lock:
            if key in self.seeded:
                return
            self.seeded.add(key)
            store = self.collections.setdefault(key, {})
            for item_id, item in items:
                store.setdefault(item_id, item)

    def insert(self, key: str, item_id: str, item: dict) -> None:
        with self._lock:
            self.seeded.add(key)  # a created item counts as "touched"
            self.collections.setdefault(key, {})[item_id] = item

    def get(self, key: str, item_id: str) -> dict | None:
        with self._lock:
            return self.collections.get(key, {}).get(item_id)

    def update(self, key: str, item_id: str, patch: dict) -> dict | None:
        with self._lock:
            item = self.collections.get(key, {}).get(item_id)
            if item is None:
                return None
            item.update(patch)
            return item

    def delete(self, key: str, item_id: str) -> bool:
        with self._lock:
            return self.collections.get(key, {}).pop(item_id, None) is not None

    def clear(self, key: str) -> None:
        with self._lock:
            self.seeded.add(key)
            self.collections[key] = {}

    def singleton(self, key: str, default: dict) -> dict:
        with self._lock:
            return self.singletons.setdefault(key, default)

    def merge_singleton(self, key: str, patch: dict[str, Any]) -> dict:
        with self._lock:
            doc = self.singletons.setdefault(key, {})
            doc.update(patch)
            return doc
