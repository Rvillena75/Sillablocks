from fastapi.testclient import TestClient
import pytest

import arduino.sila_server as server
from arduino.game.progress import ProgressStore


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
    assert village.status_code == 200
    assert "Aldea Restaurada" in village.text
    assert "Tienda de la Aldea" in village.text
    assert "shopList" in village.text


def complete_current_mission(client: TestClient) -> dict:
    payload: dict = {}
    for block in server.current_mission()["target_blocks"]:
        payload = scan(client, block)
    assert payload["status"] == "success"
    return payload


def test_reset_leaves_empty_buffer_and_initial_state() -> None:
    client = make_client()
    scan(client, "MA")

    payload = scan(client, "RESET")

    assert payload["current_blocks"] == []
    assert payload["current_text"] == ""
    assert payload["status"] == "idle"
    assert payload["feedback"] == server.FEEDBACK_EMPTY


def test_ma_and_accented_ma_produce_success() -> None:
    client = make_client()

    scan(client, "MA")
    payload = scan(client, "MÁ")

    assert payload["current_blocks"] == ["MA", "MÁ"]
    assert payload["current_text"] == "MAMÁ"
    assert payload["status"] == "success"
    assert payload["feedback"] == server.FEEDBACK_SUCCESS
    assert payload["progress_percent"] == 100
    assert payload["lumens"] == 10
    assert payload["restored_items"] == ["Farol del Bosque"]


def test_ma_and_ma_do_not_produce_success_after_enter() -> None:
    client = make_client()

    scan(client, "MA")
    scan(client, "MA")
    payload = scan(client, "ENTER")

    assert payload["current_blocks"] == ["MA", "MA"]
    assert payload["current_text"] == "MAMA"
    assert payload["status"] == "try_again"
    assert payload["feedback"] == server.FEEDBACK_TRY_AGAIN
    assert payload["progress_percent"] == 50
    assert payload["expected_next_block"] == "MÁ"


def test_delete_removes_last_block_not_last_character() -> None:
    client = make_client()

    scan(client, "MA")
    scan(client, "PA")
    payload = scan(client, "BORRAR")

    assert payload["current_blocks"] == ["MA"]
    assert payload["current_text"] == "MA"
    assert payload["status"] == "in_progress"


def test_any_normal_input_is_appended_even_if_not_suggested_for_mission() -> None:
    client = make_client()

    scan(client, "MA")
    payload_one = scan(client, "1")
    payload_g = scan(client, "G")

    assert payload_one["current_blocks"] == ["MA", "1"]
    assert payload_one["action"] == "append"
    assert payload_one["accepted"] is True
    assert payload_one["status"] == "try_again"
    assert payload_g["current_blocks"] == ["MA", "1", "G"]
    assert payload_g["action"] == "append"
    assert payload_g["accepted"] is True
    assert payload_g["status"] == "try_again"


def test_extra_block_after_success_does_not_break_mission() -> None:
    client = make_client()

    scan(client, "MA")
    scan(client, "MÁ")
    payload = scan(client, "PA")

    assert payload["current_blocks"] == ["MA", "MÁ"]
    assert payload["current_text"] == "MAMÁ"
    assert payload["status"] == "success"
    assert payload["action"] == "ignored_after_success"
    assert payload["accepted"] is False


def test_buffer_exposes_game_state_fields() -> None:
    client = make_client()
    scan(client, "MA")

    response = client.get("/buffer")

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_blocks"] == ["MA"]
    assert payload["current_text"] == "MA"
    assert payload["status"] == "in_progress"
    assert payload["feedback"] == server.FEEDBACK_IN_PROGRESS
    assert payload["zone"] == "Bosque de las Sílabas"
    assert payload["skill"] == "sílabas directas"
    assert payload["rewards"] == {
        "lumens": 0,
        "map_fragments": 0,
        "restored_items": [],
        "rewarded_mission_ids": [],
    }


def test_progress_endpoint_returns_initial_progress() -> None:
    client = make_client()

    response = client.get("/progress")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "lumens": 0,
        "fragments": 0,
        "completed_missions": [],
        "purchased_items": [],
        "unlocked_zones": ["forest"],
        "restored_items": [],
        "map_fragments": 0,
    }


def test_completed_mission_is_saved_to_progress_store() -> None:
    client = make_client()

    complete_current_mission(client)
    payload = client.get("/progress").json()

    assert payload["lumens"] == 10
    assert payload["fragments"] == 0
    assert payload["completed_missions"] == ["m001"]
    assert payload["restored_items"] == ["Farol del Bosque"]
    assert server.progress_store.load().to_dict()["completed_missions"] == ["m001"]


def test_completed_mission_returns_visual_reward_events() -> None:
    client = make_client()

    scan(client, "MA")
    payload = scan(client, "MÁ")

    assert payload["events"] == [
        {
            "type": "mission_completed",
            "mission_id": "m001",
            "target_text": "MAMÁ",
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
    payload = scan(client, "PA")
    assert payload["events"] == []

    payload = client.get("/progress").json()

    assert payload["lumens"] == 10
    assert payload["completed_missions"] == ["m001"]


def test_reset_todo_resets_persisted_progress() -> None:
    client = make_client()
    complete_current_mission(client)

    payload = scan(client, "RESET_TODO")
    progress = client.get("/progress").json()

    assert payload["lumens"] == 0
    assert progress["lumens"] == 0
    assert progress["fragments"] == 0
    assert progress["completed_missions"] == []
    assert progress["restored_items"] == []


def test_progress_tracks_fragment_rewards_after_milestone_missions() -> None:
    client = make_client()
    for _ in range(4):
        complete_current_mission(client)
        scan(client, "SIGUIENTE")
    complete_current_mission(client)

    payload = client.get("/progress").json()

    assert payload["lumens"] == 58
    assert payload["fragments"] == 2
    assert payload["map_fragments"] == 2
    assert payload["completed_missions"] == ["m001", "m002", "m003", "m004", "m005"]


def test_third_completed_mission_event_grants_fragment() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "CA")
    payload = scan(client, "SA")

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
    assert payload["resources"] == {"lumens": 0, "fragments": 0}
    item_ids = [item["item_id"] for item in payload["items"]]
    assert item_ids == [
        "small_lantern",
        "glowing_tree",
        "restored_sign",
        "decorated_house",
        "path_to_village",
        "restored_bridge",
    ]
    small_lantern = payload["items"][0]
    assert small_lantern["name"] == "Farol pequeno"
    assert small_lantern["cost"] == {"lumens": 8, "fragments": 0}
    assert small_lantern["purchased"] is False
    assert small_lantern["affordable"] is False


def test_buy_lumen_item_spends_persists_and_returns_events() -> None:
    client = make_client()
    complete_current_mission(client)

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["code"] == "purchased"
    assert payload["item"]["item_id"] == "small_lantern"
    assert payload["item"]["purchased"] is True
    assert payload["progress"]["lumens"] == 2
    assert payload["progress"]["fragments"] == 0
    assert payload["progress"]["purchased_items"] == ["small_lantern"]
    assert "small_lantern" in payload["progress"]["restored_items"]
    assert payload["events"] == [
        {
            "type": "item_purchased",
            "item_id": "small_lantern",
            "name": "Farol pequeno",
            "spent": {"lumens": 8, "fragments": 0},
        },
        {
            "type": "village_restored",
            "item_id": "small_lantern",
            "name": "Farol pequeno",
        },
    ]
    assert server.progress_store.load().lumens == 2
    assert server.progress_store.load().purchased_items == ["small_lantern"]


def test_buy_fragment_item_unlocks_zone_and_persists() -> None:
    client = make_client()
    for _ in range(2):
        complete_current_mission(client)
        scan(client, "SIGUIENTE")
    complete_current_mission(client)

    response = client.post("/buy", json={"item_id": "path_to_village"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["progress"]["fragments"] == 0
    assert payload["progress"]["purchased_items"] == ["path_to_village"]
    assert payload["progress"]["unlocked_zones"] == ["forest", "village"]
    assert payload["events"][-1] == {
        "type": "zone_unlocked",
        "zone_id": "village",
    }


def test_buy_rejects_insufficient_resources_without_spending() -> None:
    client = make_client()

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "not_enough_resources"
    assert payload["progress"]["lumens"] == 0
    assert payload["progress"]["purchased_items"] == []
    assert payload["events"] == []


def test_buy_rejects_duplicate_purchase_without_spending_again() -> None:
    client = make_client()
    complete_current_mission(client)
    first = client.post("/buy", json={"item_id": "small_lantern"}).json()

    response = client.post("/buy", json={"item_id": "small_lantern"})

    assert first["progress"]["lumens"] == 2
    assert response.status_code == 409
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "already_purchased"
    assert payload["progress"]["lumens"] == 2
    assert payload["progress"]["purchased_items"] == ["small_lantern"]


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
    assert payload["available_blocks"] == ["PA", "PÁ", "MA", "SA"]


def test_next_does_not_advance_before_success() -> None:
    client = make_client()
    scan(client, "MA")

    payload = scan(client, "SIGUIENTE")

    assert payload["mission_id"] == "m001"
    assert payload["mission_number"] == 1
    assert payload["current_blocks"] == ["MA"]
    assert payload["status"] == "in_progress"
    assert payload["feedback"] == server.FEEDBACK_NEXT_BLOCKED
    assert payload["accepted"] is False


def test_reset_restarts_current_mission_without_returning_to_first() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    scan(client, "PA")

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
    scan(client, "PA")

    payload = scan(client, "RESET_TODO")

    assert payload["mission_id"] == "m001"
    assert payload["mission_number"] == 1
    assert payload["completed_missions"] == 0
    assert payload["current_blocks"] == []
    assert payload["status"] == "idle"
    assert payload["lumens"] == 0
    assert payload["restored_items"] == []


def test_post_nfc_accepts_json_body() -> None:
    client = make_client()

    response = client.post("/nfc", json={"letra": "MA"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_blocks"] == ["MA"]
    assert payload["action"] == "append"


def test_papa_validates_correctly_in_second_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "PA")
    payload = scan(client, "PÁ")

    assert payload["mission_id"] == "m002"
    assert payload["current_blocks"] == ["PA", "PÁ"]
    assert payload["current_text"] == "PAPÁ"
    assert payload["status"] == "success"


def test_casa_validates_correctly_in_third_mission() -> None:
    client = make_client()
    complete_current_mission(client)
    scan(client, "SIGUIENTE")
    complete_current_mission(client)
    scan(client, "SIGUIENTE")

    scan(client, "CA")
    payload = scan(client, "SA")

    assert payload["mission_id"] == "m003"
    assert payload["current_blocks"] == ["CA", "SA"]
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

    scan(client, "ME")
    payload = scan(client, "SA")

    assert payload["mission_id"] == "m004"
    assert payload["current_blocks"] == ["ME", "SA"]
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
    assert payload["lumens"] == 58
    assert payload["map_fragments"] == 2
