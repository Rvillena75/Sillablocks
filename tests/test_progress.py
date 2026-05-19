import json

import pytest

from arduino.game.progress import (
    DEFAULT_UNLOCKED_ZONES,
    DEVELOPMENT_STARTING_FRAGMENTS,
    DEVELOPMENT_STARTING_LUMENS,
    GameProgress,
    ProgressStore,
)


def test_progress_store_creates_default_file(tmp_path) -> None:
    state_path = tmp_path / "game_state.json"
    store = ProgressStore(state_path)

    progress = store.load()

    assert progress.to_dict() == {
        "lumens": DEVELOPMENT_STARTING_LUMENS,
        "fragments": DEVELOPMENT_STARTING_FRAGMENTS,
        "completed_missions": [],
        "purchased_items": [],
        "unlocked_zones": DEFAULT_UNLOCKED_ZONES,
        "restored_items": [],
        "placed_decorations": [],
    }
    assert json.loads(state_path.read_text(encoding="utf-8")) == progress.to_dict()


def test_progress_store_saves_and_loads_progress(tmp_path) -> None:
    store = ProgressStore(tmp_path / "game_state.json")
    progress = GameProgress(lumens=0, fragments=0)
    progress.add_rewards(lumens=8, fragments=1)
    progress.mark_mission_completed("m001")
    progress.mark_item_purchased("small_lantern")
    progress.mark_item_purchased("small_lantern")
    progress.unlock_zone("village")
    progress.mark_item_restored("forest_lantern")
    progress.placed_decorations.append(
        {
            "id": "decor_001",
            "item_id": "small_lantern",
            "position": {"x": 44, "y": 72},
            "rotation": 0,
            "scale": 1,
        }
    )

    store.save(progress)
    loaded = store.load()

    assert loaded.to_dict() == {
        "lumens": 8,
        "fragments": 1,
        "completed_missions": ["m001"],
        "purchased_items": ["small_lantern", "small_lantern"],
        "unlocked_zones": ["forest", "village"],
        "restored_items": ["forest_lantern"],
        "placed_decorations": [
            {
                "id": "decor_001",
                "item_id": "small_lantern",
                "position": {"x": 44, "y": 72},
                "rotation": 0,
                "scale": 1,
            }
        ],
    }


def test_progress_from_dict_normalizes_invalid_values() -> None:
    progress = GameProgress.from_dict(
        {
            "lumens": -10,
            "map_fragments": "2",
            "completed_missions": ["m001", "m001", "", 7],
            "purchased_items": "small_lantern",
            "unlocked_zones": [],
            "restored_items": ["forest_lantern", "forest_lantern"],
            "placed_decorations": [
                {
                    "id": "decor_001",
                    "item_id": "small_lantern",
                    "position": {"x": 120, "y": "80"},
                },
                {
                    "id": "decor_001",
                    "item_id": "duplicate",
                    "position": {"x": 10, "y": 10},
                },
                {"id": "missing_position", "item_id": "bad"},
            ],
        }
    )

    assert progress.to_dict() == {
        "lumens": 0,
        "fragments": 2,
        "completed_missions": ["m001"],
        "purchased_items": [],
        "unlocked_zones": ["forest"],
        "restored_items": ["forest_lantern"],
        "placed_decorations": [
            {
                "id": "decor_001",
                "item_id": "small_lantern",
                "position": {"x": 100, "y": 80},
                "rotation": 0,
                "scale": 1,
            }
        ],
    }


def test_progress_store_update_loads_mutates_and_persists(tmp_path) -> None:
    store = ProgressStore(tmp_path / "game_state.json")

    updated = store.update(lambda progress: progress.add_rewards(lumens=10, fragments=2))

    assert updated.lumens == DEVELOPMENT_STARTING_LUMENS + 10
    assert updated.fragments == DEVELOPMENT_STARTING_FRAGMENTS + 2
    assert store.load().to_dict() == updated.to_dict()


def test_progress_store_rejects_invalid_json(tmp_path) -> None:
    state_path = tmp_path / "game_state.json"
    state_path.write_text("{", encoding="utf-8")
    store = ProgressStore(state_path)

    with pytest.raises(ValueError, match="Invalid progress JSON"):
        store.load()
