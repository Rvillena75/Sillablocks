from fastapi.testclient import TestClient

import arduino.sila_server as server


def reset_server_state() -> None:
    server.current_blocks.clear()
    server.current_mission_index = 0
    server.completed_mission_ids.clear()
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
