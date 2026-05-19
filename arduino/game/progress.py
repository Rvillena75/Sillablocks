from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


DEFAULT_UNLOCKED_ZONES = ["forest"]
DEFAULT_STATE_PATH = Path(__file__).resolve().parents[1] / "game_state.json"
DEVELOPMENT_STARTING_LUMENS = 99
DEVELOPMENT_STARTING_FRAGMENTS = 99


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


def _as_inventory_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if cleaned:
            items.append(cleaned)
    return items


def _as_placed_decorations(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    decorations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue

        item_id = str(item.get("item_id", "")).strip()
        decoration_id = str(item.get("id", "")).strip() or f"decor_{index:03d}"
        position = item.get("position")
        if not item_id or decoration_id in seen or not isinstance(position, dict):
            continue

        x = _as_non_negative_int(position.get("x"), default=50)
        y = _as_non_negative_int(position.get("y"), default=70)
        decorations.append(
            {
                "id": decoration_id,
                "item_id": item_id,
                "position": {"x": min(x, 100), "y": min(y, 100)},
                "rotation": _as_non_negative_int(item.get("rotation"), default=0),
                "scale": max(_as_non_negative_int(item.get("scale"), default=1), 1),
            }
        )
        seen.add(decoration_id)
    return decorations


@dataclass
class GameProgress:
    lumens: int = DEVELOPMENT_STARTING_LUMENS
    fragments: int = DEVELOPMENT_STARTING_FRAGMENTS
    completed_missions: list[str] = field(default_factory=list)
    purchased_items: list[str] = field(default_factory=list)
    unlocked_zones: list[str] = field(default_factory=lambda: list(DEFAULT_UNLOCKED_ZONES))
    restored_items: list[str] = field(default_factory=list)
    placed_decorations: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def default(cls) -> "GameProgress":
        return cls()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameProgress":
        return cls(
            lumens=_as_non_negative_int(
                payload.get("lumens"),
                default=DEVELOPMENT_STARTING_LUMENS,
            ),
            fragments=_as_non_negative_int(
                payload.get("fragments", payload.get("map_fragments")),
                default=DEVELOPMENT_STARTING_FRAGMENTS,
            ),
            completed_missions=_as_string_list(payload.get("completed_missions")),
            purchased_items=_as_inventory_list(payload.get("purchased_items")),
            unlocked_zones=(
                _as_string_list(payload.get("unlocked_zones")) or list(DEFAULT_UNLOCKED_ZONES)
            ),
            restored_items=_as_string_list(payload.get("restored_items")),
            placed_decorations=_as_placed_decorations(payload.get("placed_decorations")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lumens": self.lumens,
            "fragments": self.fragments,
            "completed_missions": list(self.completed_missions),
            "purchased_items": list(self.purchased_items),
            "unlocked_zones": list(self.unlocked_zones),
            "restored_items": list(self.restored_items),
            "placed_decorations": list(self.placed_decorations),
        }

    def add_rewards(self, lumens: int = 0, fragments: int = 0) -> None:
        self.lumens += max(lumens, 0)
        self.fragments += max(fragments, 0)

    def mark_mission_completed(self, mission_id: str) -> None:
        self._append_unique(self.completed_missions, mission_id)

    def mark_item_purchased(self, item_id: str) -> None:
        cleaned = item_id.strip()
        if cleaned:
            self.purchased_items.append(cleaned)

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
