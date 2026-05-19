from fastapi.testclient import TestClient
import pytest

import arduino.sila_server as server
from arduino.game.progress import GameProgress, ProgressStore


@pytest.fixture(autouse=True)
def isolated_progress_store(tmp_path):
    original_store = server.progress_store
    server.progress_store = ProgressStore(tmp_path / "game_state.json")
    server.reset_runtime_state()
    yield
    server.progress_store = original_store
    server.game_engine.reset_runtime()
    server.load_persisted_progress()


def reset_server_state() -> None:
    server.reset_runtime_state()


def make_client() -> TestClient:
    reset_server_state()
    return TestClient(server.app)


def scan(client: TestClient, value: str) -> dict:
    response = client.get("/nfc", params={"letra": value})
    assert response.status_code == 200
    return response.json()


def test_health_responds_correctly() -> None:
    client = make_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "status": "ok",
        "service": "sillablocks",
        "mission_id": "m001",
    }


def test_index_and_village_pages_render() -> None:
    client = make_client()

    index = client.get("/")
    village = client.get("/aldea")

    assert index.status_code == 200
    assert "Estado técnico" in index.text
    assert "Cubos sugeridos" in index.text
    assert "missionRestoration" in index.text
    assert "restorationMeter" in index.text
    assert "lumoLine" in index.text
    assert "rewardRibbon" not in index.text
    assert "resource-lumens" not in index.text
    assert village.status_code == 200
    assert "Aldea de Lumo" in village.text
    assert "Sala de trofeos" in village.text
    assert "Decoraciones" in village.text
    assert "Objetos funcionales" in village.text
    assert "villageLumoLine" in village.text
    assert "villageMist" in village.text
    assert "villageMissionCard" in village.text
    assert "missionCardObjective" in village.text
    assert "shopList" in village.text
    assert "resourceLumens" in village.text
    assert "resourceFragments" in village.text
    assert "placedDecorationsLayer" in village.text
    assert "decorationPreview" in village.text
    assert "editVillageMode" in village.text
    assert "decorationInventoryTray" in village.text
    assert ">Juego<" not in village.text
    assert "missionCardBuffer" not in village.text
    assert "missionCardValidate" not in village.text
    assert "missionCardNext" not in village.text
    assert "nextMissionCard" not in village.text


def complete_current_mission(client: TestClient) -> dict:
    payload: dict = {}
    for block in server.current_mission()["target_blocks"]:
        payload = scan(client, block)
    assert payload["status"] == "success"
    return payload


def test_reset_leaves_empty_buffer_and_initial_state() -> None:
    client = make_client()
    scan(client, "M")

    payload = scan(client, "RESET")

    assert payload["current_blocks"] == []
    assert payload["current_text"] == ""
    assert payload["status"] == "idle"
    assert payload["feedback"] == server.FEEDBACK_EMPTY


def test_letters_mama_produce_success() -> None:
    client = make_client()

    scan(client, "M")
    scan(client, "A")
    scan(client, "M")
    payload = scan(client, "A")

    assert payload["current_blocks"] == ["M", "A", "M", "A"]
    assert payload["current_text"] == "MAMA"
    assert payload["status"] == "success"
    assert payload["feedback"] == server.FEEDBACK_SUCCESS
    assert payload["progress_percent"] == 100
    assert payload["lumens"] == 109
    assert payload["restored_items"] == ["Farol del Bosque"]


def test_partial_mama_does_not_produce_success_after_enter() -> None:
    client = make_client()

    scan(client, "M")
    scan(client, "A")
    payload = scan(client, "ENTER")

    assert payload["current_blocks"] == ["M", "A"]
    assert payload["current_text"] == "MA"
    assert payload["status"] == "try_again"
    assert payload["feedback"] == server.FEEDBACK_TRY_AGAIN
    assert payload["progress_percent"] == 50
    assert payload["expected_next_block"] == "M"


def test_delete_removes_last_block_not_last_character() -> None:
    client = make_client()

    scan(client, "M")
    scan(client, "A")
    payload = scan(client, "BORRAR")

    assert payload["current_blocks"] == ["M"]
    assert payload["current_text"] == "M"
    assert payload["status"] == "in_progress"


def test_any_normal_input_is_appended_even_if_not_suggested_for_mission() -> None:
    client = make_client()

    scan(client, "M")
    payload_one = scan(client, "1")
    payload_g = scan(client, "G")

    assert payload_one["current_blocks"] == ["M", "1"]
    assert payload_one["action"] == "append"
    assert payload_one["accepted"] is True
    assert payload_one["status"] == "try_again"
    assert payload_g["current_blocks"] == ["M", "1", "G"]
    assert payload_g["action"] == "append"
    assert payload_g["accepted"] is True
    assert payload_g["status"] == "try_again"


def test_extra_block_after_success_does_not_break_mission() -> None:
    client = make_client()

    scan(client, "M")
    scan(client, "A")
    scan(client, "M")
    scan(client, "A")
    payload = scan(client, "P")

    assert payload["current_blocks"] == ["M", "A", "M", "A"]
    assert payload["current_text"] == "MAMA"
    assert payload["status"] == "success"
    assert payload["action"] == "ignored_after_success"
    assert payload["accepted"] is False


def test_buffer_exposes_game_state_fields() -> None:
    client = make_client()
    scan(client, "M")

    response = client.get("/buffer")

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_blocks"] == ["M"]
    assert payload["current_text"] == "M"
    assert payload["status"] == "in_progress"
    assert payload["feedback"] == server.FEEDBACK_IN_PROGRESS
    assert payload["zone"] == "Bosque de las Sílabas"
    assert payload["skill"] == "letras individuales"
    assert payload["rewards"] == {
        "lumens": 99,
        "map_fragments": 99,
        "restored_items": [],
        "rewarded_mission_ids": [],
    }


def test_progress_endpoint_returns_initial_progress() -> None:
    client = make_client()

    response = client.get("/progress")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "lumens": 99,
        "fragments": 99,
        "completed_missions": [],
        "purchased_items": [],
        "unlocked_zones": ["forest"],
        "restored_items": [],
        "placed_decorations": [],
        "map_fragments": 99,
    }


def test_startup_reset_clears_persisted_progress() -> None:
    progress = GameProgress(lumens=12, fragments=2)
    progress.mark_mission_completed("m001")
    progress.mark_item_restored("Farol del Bosque")
    server.progress_store.save(progress)
    server.load_persisted_progress()
    assert server.game_engine.lumens == 12

    reset_progress = server.reset_demo_state_on_startup()

    expected = GameProgress.default().to_dict()
    assert reset_progress.to_dict() == expected
    assert server.progress_store.load().to_dict() == expected
    assert server.game_engine.lumens == 99
    assert server.game_engine.completed_mission_ids == set()


def test_completed_mission_is_saved_to_progress_store() -> None:
    client = make_client()

    complete_current_mission(client)
    payload = client.get("/progress").json()

    assert payload["lumens"] == 109
    assert payload["fragments"] == 99
    assert payload["completed_missions"] == ["m001"]
    assert payload["restored_items"] == ["Farol del Bosque"]
    assert server.progress_store.load().to_dict()["completed_missions"] == ["m001"]


def test_completed_mission_returns_visual_reward_events() -> None:
    client = make_client()

    scan(client, "M")
    scan(client, "A")
    scan(client, "M")
    payload = scan(client, "A")

    assert payload["events"] == [
        {
            "type": "mission_completed",
            "mission_id": "m001",
            "target_text": "MAMA",
        },
        {
            "type": "reward_granted",
            "mission_id": "m001",
            "lumens": 10,
            "fragments": 0,
        },
        {
            "type": "scene_restored",
            "mission_id": "m001",
            "item": "Farol del Bosque",
        },
    ]


def test_progress_does_not_duplicate_rewards_after_success() -> None:
    client = make_client()

    complete_current_mission(client)
    payload = scan(client, "P")
    assert payload["events"] == []

    payload = client.get("/progress").json()

    assert payload["lumens"] == 109
    assert payload["completed_missions"] == ["m001"]


def test_reset_todo_resets_persisted_progress() -> None:
    client = make_client()
    complete_current_mission(client)

    payload = scan(client, "RESET_TODO")
    progress = client.get("/progress").json()

    assert len(payload["recent_inputs"]) == 1
    assert payload["recent_inputs"][0]["value"] == "RESET_TODO"
    assert payload["recent_inputs"][0]["action"] == "reset_all"
    assert payload["recent_inputs"][0]["accepted"] is True
    assert payload["lumens"] == 99
    assert progress["lumens"] == 99
    assert progress["fragments"] == 99
    assert progress["completed_missions"] == []
    assert progress["restored_items"] == []
    assert progress["placed_decorations"] == []


def test_progress_tracks_fragment_rewards_after_milestone_missions() -> None:
    client = make_client()
    for _ in range(4):
        complete_current_mission(client)
        scan(client, "SIGUIENTE")
    complete_current_mission(client)

    payload = client.get("/progress").json()

    assert payload["lumens"] == 157
    assert payload["fragments"] == 101
    assert payload["map_fragments"] == 101
    assert payload["completed_missions"] == ["m001", "m002", "m003", "m004", "m005"]


def test_third_completed_mission_event_grants_fragment() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "C")
    scan(client, "A")
    scan(client, "S")
    payload = scan(client, "A")

    reward_event = next(event for event in payload["events"] if event["type"] == "reward_granted")
    assert reward_event == {
        "type": "reward_granted",
        "mission_id": "m003",
        "lumens": 12,
        "fragments": 1,
    }


def test_shop_endpoint_exposes_inventory_and_affordability() -> None:
    client = make_client()

    response = client.get("/shop")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["resources"] == {"lumens": 99, "fragments": 99}
    item_ids = [item["item_id"] for item in payload["items"]]
    assert item_ids == [
        "small_lantern",
        "glowing_tree",
        "restored_sign",
        "decorated_house",
        "path_to_village",
        "restored_bridge",
    ]
    assert all(item["category"] == "decoration" for item in payload["items"])
    assert all(item["restores_item"] is None for item in payload["items"])
    assert all(item["unlocks_zone"] is None for item in payload["items"])
    small_lantern = payload["items"][0]
    assert small_lantern["name"] == "Farol de luciernagas"
    assert small_lantern["cost"] == {"lumens": 6, "fragments": 0}
    assert small_lantern["purchased"] is False
    assert small_lantern["affordable"] is True
    assert small_lantern["placed"] is False
    assert small_lantern["owned_count"] == 0
    assert small_lantern["placed_count"] == 0
    assert small_lantern["available_to_place"] == 0


def test_buy_lumen_item_spends_persists_and_returns_events() -> None:
    client = make_client()

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["code"] == "purchased"
    assert payload["item"]["item_id"] == "small_lantern"
    assert payload["item"]["purchased"] is True
    assert payload["progress"]["lumens"] == 93
    assert payload["progress"]["fragments"] == 99
    assert payload["progress"]["purchased_items"] == ["small_lantern"]
    assert payload["progress"]["restored_items"] == []
    assert payload["progress"]["placed_decorations"] == []
    assert payload["events"] == [
        {
            "type": "item_purchased",
            "item_id": "small_lantern",
            "name": "Farol de luciernagas",
            "spent": {"lumens": 6, "fragments": 0},
        },
    ]
    assert server.progress_store.load().lumens == 93
    assert server.progress_store.load().purchased_items == ["small_lantern"]


def test_buy_decoration_does_not_unlock_zone_or_restore_functional_object() -> None:
    client = make_client()

    response = client.post("/buy", json={"item_id": "path_to_village"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["progress"]["lumens"] == 91
    assert payload["progress"]["fragments"] == 99
    assert payload["progress"]["purchased_items"] == ["path_to_village"]
    assert payload["progress"]["unlocked_zones"] == ["forest"]
    assert payload["progress"]["restored_items"] == []
    assert payload["progress"]["placed_decorations"] == []
    assert payload["events"] == [
        {
            "type": "item_purchased",
            "item_id": "path_to_village",
            "name": "Cerca de madera",
            "spent": {"lumens": 8, "fragments": 0},
        }
    ]


def test_buy_rejects_insufficient_resources_without_spending() -> None:
    client = make_client()
    server.progress_store.save(GameProgress(lumens=0, fragments=0))

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "not_enough_resources"
    assert payload["progress"]["lumens"] == 0
    assert payload["progress"]["purchased_items"] == []
    assert payload["events"] == []


def test_buy_allows_multiple_copies_of_same_decoration() -> None:
    client = make_client()
    first = client.post("/buy", json={"item_id": "small_lantern"}).json()

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert first["progress"]["lumens"] == 93
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["code"] == "purchased"
    assert payload["progress"]["lumens"] == 87
    assert payload["progress"]["purchased_items"] == ["small_lantern", "small_lantern"]
    assert payload["item"]["owned_count"] == 2
    assert payload["item"]["available_to_place"] == 2


def test_place_move_and_remove_decoration_persists_without_restoring_world() -> None:
    client = make_client()
    client.post("/buy", json={"item_id": "small_lantern"})

    placed_response = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 46, "y": 74},
    )

    assert placed_response.status_code == 200
    placed = placed_response.json()
    assert placed["ok"] is True
    assert placed["decoration"] == {
        "id": "decor_001",
        "item_id": "small_lantern",
        "position": {"x": 46, "y": 74},
        "rotation": 0,
        "scale": 1,
    }
    assert placed["progress"]["placed_decorations"] == [placed["decoration"]]
    assert placed["progress"]["restored_items"] == []

    shop_after_place = client.get("/shop").json()
    small_lantern = shop_after_place["items"][0]
    assert small_lantern["purchased"] is True
    assert small_lantern["placed"] is True
    assert small_lantern["owned_count"] == 1
    assert small_lantern["placed_count"] == 1
    assert small_lantern["available_to_place"] == 0

    moved_response = client.patch(
        "/decorations/decor_001",
        json={"x": 62, "y": 81},
    )

    assert moved_response.status_code == 200
    moved = moved_response.json()
    assert moved["decoration"]["position"] == {"x": 62, "y": 81}
    assert moved["progress"]["placed_decorations"][0]["position"] == {"x": 62, "y": 81}

    removed_response = client.delete("/decorations/decor_001")

    assert removed_response.status_code == 200
    removed = removed_response.json()
    assert removed["ok"] is True
    assert removed["progress"]["purchased_items"] == ["small_lantern"]
    assert removed["progress"]["placed_decorations"] == []


def test_place_decoration_rejects_unowned_and_out_of_bounds_but_allows_extra_owned_copy() -> None:
    client = make_client()

    unowned = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 50, "y": 70},
    )
    assert unowned.status_code == 409
    assert unowned.json()["ok"] is False

    client.post("/buy", json={"item_id": "small_lantern"})
    out_of_bounds = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 150, "y": 70},
    )
    assert out_of_bounds.status_code == 400

    first_placed = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 50, "y": 70},
    )
    assert first_placed.status_code == 200

    no_inventory_left = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 60, "y": 75},
    )
    assert no_inventory_left.status_code == 409
    assert no_inventory_left.json()["progress"]["placed_decorations"][0]["position"] == {"x": 50, "y": 70}

    client.post("/buy", json={"item_id": "small_lantern"})
    second_placed = client.post(
        "/decorations/place",
        json={"item_id": "small_lantern", "x": 60, "y": 75},
    )
    assert second_placed.status_code == 200
    assert [item["id"] for item in second_placed.json()["progress"]["placed_decorations"]] == [
        "decor_001",
        "decor_002",
    ]


def test_buy_rejects_unknown_item() -> None:
    client = make_client()

    response = client.post("/buy", json={"item_id": "missing_item"})

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "unknown_item"
    assert payload["item"] is None


def test_next_advances_after_success() -> None:
    client = make_client()
    complete_current_mission(client)

    payload = scan(client, "SIGUIENTE")

    assert payload["mission_id"] == "m002"
    assert payload["mission_number"] == 2
    assert payload["total_missions"] == 5
    assert payload["completed_missions"] == 1
    assert payload["current_blocks"] == []
    assert payload["status"] == "idle"
    assert payload["available_blocks"] == ["P", "A", "M", "S"]


def test_select_mission_advances_to_unlocked_mission() -> None:
    client = make_client()
    complete_current_mission(client)

    response = client.post("/mission/select", json={"mission_id": "m002"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["selected"] is True
    assert payload["mission_id"] == "m002"
    assert payload["mission_number"] == 2
    assert payload["current_blocks"] == []
    assert payload["status"] == "idle"


def test_select_mission_rejects_locked_mission() -> None:
    client = make_client()

    response = client.post("/mission/select", json={"mission_id": "m003"})

    assert response.status_code == 409
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "mission_locked"
    assert server.game_engine.current_mission().mission_id == "m001"


def test_select_mission_rejects_unknown_mission() -> None:
    client = make_client()

    response = client.post("/mission/select", json={"mission_id": "m999"})

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "unknown_mission"


def test_next_does_not_advance_before_success() -> None:
    client = make_client()
    scan(client, "M")

    payload = scan(client, "SIGUIENTE")

    assert payload["mission_id"] == "m001"
    assert payload["mission_number"] == 1
    assert payload["current_blocks"] == ["M"]
    assert payload["status"] == "in_progress"
    assert payload["feedback"] == server.FEEDBACK_NEXT_BLOCKED
    assert payload["accepted"] is False


def test_reset_restarts_current_mission_without_returning_to_first() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    scan(client, "P")

    payload = scan(client, "RESET")

    assert payload["mission_id"] == "m002"
    assert payload["mission_number"] == 2
    assert payload["completed_missions"] == 1
    assert payload["current_blocks"] == []
    assert payload["status"] == "idle"


def test_reset_all_returns_to_first_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    scan(client, "P")

    payload = scan(client, "RESET_TODO")

    assert payload["mission_id"] == "m001"
    assert payload["mission_number"] == 1
    assert payload["completed_missions"] == 0
    assert payload["current_blocks"] == []
    assert payload["status"] == "idle"
    assert payload["lumens"] == 99
    assert payload["restored_items"] == []


def test_post_nfc_accepts_json_body() -> None:
    client = make_client()

    response = client.post("/nfc", json={"letra": "M"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_blocks"] == ["M"]
    assert payload["action"] == "append"


def test_papa_validates_correctly_in_second_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "P")
    scan(client, "A")
    scan(client, "P")
    payload = scan(client, "A")

    assert payload["mission_id"] == "m002"
    assert payload["current_blocks"] == ["P", "A", "P", "A"]
    assert payload["current_text"] == "PAPA"
    assert payload["status"] == "success"


def test_casa_validates_correctly_in_third_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "C")
    scan(client, "A")
    scan(client, "S")
    payload = scan(client, "A")

    assert payload["mission_id"] == "m003"
    assert payload["current_blocks"] == ["C", "A", "S", "A"]
    assert payload["current_text"] == "CASA"
    assert payload["status"] == "success"


def test_mesa_validates_correctly_in_fourth_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "M")
    scan(client, "E")
    scan(client, "S")
    payload = scan(client, "A")

    assert payload["mission_id"] == "m004"
    assert payload["current_blocks"] == ["M", "E", "S", "A"]
    assert payload["current_text"] == "MESA"
    assert payload["status"] == "success"


def test_bota_validates_correctly_in_fifth_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "B")
    scan(client, "O")
    scan(client, "T")
    payload = scan(client, "A")

    assert payload["mission_id"] == "m005"
    assert payload["current_blocks"] == ["B", "O", "T", "A"]
    assert payload["current_text"] == "BOTA"
    assert payload["status"] == "success"
    assert payload["available_blocks"] == ["B", "O", "T", "A"]


def test_next_after_last_success_marks_demo_complete() -> None:
    client = make_client()
    for _ in range(4):
        complete_current_mission(client)
        scan(client, "SIGUIENTE")
    complete_current_mission(client)

    payload = scan(client, "SIGUIENTE")

    assert payload["mission_id"] == "m005"
    assert payload["status"] == "demo_complete"
    assert payload["is_demo_complete"] is True
    assert payload["is_last_mission"] is True
    assert payload["completed_missions"] == 5
    assert payload["lumens"] == 157
    assert payload["map_fragments"] == 101
