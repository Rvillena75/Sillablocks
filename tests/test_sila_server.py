from fastapi.testclient import TestClient

import arduino.sila_server as server


def reset_server_state() -> None:
    server.current_blocks.clear()
    server.last_input = None
    server.last_received_input = None
    server.last_ignored_input = None
    server.last_action = "init"
    server.game_status = "idle"
    server.feedback = server.FEEDBACK_EMPTY
    server.recent_inputs.clear()


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


def test_unavailable_input_is_ignored_and_does_not_change_buffer() -> None:
    client = make_client()

    scan(client, "MA")
    payload_one = scan(client, "1")
    payload_g = scan(client, "G")

    assert payload_one["current_blocks"] == ["MA"]
    assert payload_one["action"] == "ignored"
    assert payload_one["accepted"] is False
    assert payload_g["current_blocks"] == ["MA"]
    assert payload_g["action"] == "ignored"
    assert payload_g["accepted"] is False


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
