from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


DEFAULT_UNLOCKED_ZONES = ["forest"]
DEFAULT_STATE_PATH = Path(__file__).resolve().parents[1] / "game_state.json"


def _as_non_negative_int(value: Any, default: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, 0)


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    items: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        items.append(cleaned)
        seen.add(cleaned)
    return items


@dataclass
class GameProgress:
    lumens: int = 0
    fragments: int = 0
    completed_missions: list[str] = field(default_factory=list)
    purchased_items: list[str] = field(default_factory=list)
    unlocked_zones: list[str] = field(default_factory=lambda: list(DEFAULT_UNLOCKED_ZONES))
    restored_items: list[str] = field(default_factory=list)

    @classmethod
    def default(cls) -> "GameProgress":
        return cls()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameProgress":
        return cls(
            lumens=_as_non_negative_int(payload.get("lumens")),
            fragments=_as_non_negative_int(
                payload.get("fragments", payload.get("map_fragments"))
            ),
            completed_missions=_as_string_list(payload.get("completed_missions")),
            purchased_items=_as_string_list(payload.get("purchased_items")),
            unlocked_zones=(
                _as_string_list(payload.get("unlocked_zones")) or list(DEFAULT_UNLOCKED_ZONES)
            ),
            restored_items=_as_string_list(payload.get("restored_items")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lumens": self.lumens,
            "fragments": self.fragments,
            "completed_missions": list(self.completed_missions),
            "purchased_items": list(self.purchased_items),
            "unlocked_zones": list(self.unlocked_zones),
            "restored_items": list(self.restored_items),
        }

    def add_rewards(self, lumens: int = 0, fragments: int = 0) -> None:
        self.lumens += max(lumens, 0)
        self.fragments += max(fragments, 0)

    def mark_mission_completed(self, mission_id: str) -> None:
        self._append_unique(self.completed_missions, mission_id)

    def mark_item_purchased(self, item_id: str) -> None:
        self._append_unique(self.purchased_items, item_id)

    def unlock_zone(self, zone_id: str) -> None:
        self._append_unique(self.unlocked_zones, zone_id)

    def mark_item_restored(self, item_id: str) -> None:
        self._append_unique(self.restored_items, item_id)

    @staticmethod
    def _append_unique(items: list[str], value: str) -> None:
        cleaned = value.strip()
        if cleaned and cleaned not in items:
            items.append(cleaned)


class ProgressStore:
    def __init__(self, path: Path | str = DEFAULT_STATE_PATH) -> None:
        self.path = Path(path)

    def load(self) -> GameProgress:
        if not self.path.exists():
            progress = GameProgress.default()
            self.save(progress)
            return progress

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid progress JSON at {self.path}") from exc

        if not isinstance(payload, dict):
            raise ValueError(f"Progress JSON must be an object at {self.path}")

        return GameProgress.from_dict(payload)

    def save(self, progress: GameProgress) -> GameProgress:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(progress.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return progress

    def reset(self) -> GameProgress:
        return self.save(GameProgress.default())

    def update(self, callback: Callable[[GameProgress], None]) -> GameProgress:
        progress = self.load()
        callback(progress)
        return self.save(progress)
