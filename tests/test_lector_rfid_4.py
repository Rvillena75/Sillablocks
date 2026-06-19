from __future__ import annotations

import importlib.util
import threading
import time
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "arduino" / "4rfid" / "lector_rfid.py"
spec = importlib.util.spec_from_file_location("lector_rfid_4", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
lector_rfid_4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lector_rfid_4)


def test_parse_slot_line_accepts_reader_slot_and_uid() -> None:
    assert lector_rfid_4.parse_slot_line("SLOT,2, da:e9-c1 03 ") == (2, "DAE9C103")


def test_parse_slot_line_accepts_empty_reader_slot() -> None:
    assert lector_rfid_4.parse_slot_line("SLOT,1,") == (1, "")


def test_parse_slot_line_rejects_status_output() -> None:
    assert lector_rfid_4.parse_slot_line("SILABLOCKS_4RFID_READY") is None
    assert lector_rfid_4.parse_slot_line("SLOT,5,DAE9C103") is None


def test_slot_values_from_uids_uses_configured_uid_map() -> None:
    uid_map = {"DAE9C103": "B", "9EE9C103": "A"}

    values = lector_rfid_4.slot_values_from_uids(
        ["DAE9C103", "", "MISSING", "9EE9C103"],
        uid_map,
    )

    assert values == ["B", "", "", "A"]


class RecordingDispatcher:
    def __init__(self) -> None:
        self.slot_events: list[list[str]] = []
        self.arcade_events = 0

    def publish_slots(self, slot_values: list[str]) -> None:
        self.slot_events.append(list(slot_values))

    def publish_arcade(self) -> None:
        self.arcade_events += 1


def test_process_line_dispatches_slot_without_waiting_for_http() -> None:
    dispatcher = RecordingDispatcher()
    slot_uids = ["", "", "", ""]

    handled = lector_rfid_4.process_line(
        "SLOT,0,DAE9C103",
        slot_uids,
        {"DAE9C103": "B"},
        "http://localhost:5000",
        False,
        dispatcher,
    )

    assert handled is True
    assert slot_uids == ["DAE9C103", "", "", ""]
    assert dispatcher.slot_events == [["B", "", "", ""]]


def test_process_line_ignores_duplicate_slot_state() -> None:
    dispatcher = RecordingDispatcher()
    slot_uids = ["DAE9C103", "", "", ""]

    lector_rfid_4.process_line(
        "SLOT,0,DAE9C103",
        slot_uids,
        {"DAE9C103": "B"},
        "http://localhost:5000",
        False,
        dispatcher,
    )

    assert dispatcher.slot_events == []


def test_process_line_dispatches_button_without_waiting_for_http() -> None:
    dispatcher = RecordingDispatcher()

    lector_rfid_4.process_line(
        "BUTTON,ENTER",
        ["", "", "", ""],
        {},
        "http://localhost:5000",
        False,
        dispatcher,
    )

    assert dispatcher.arcade_events == 1


class RecordingHttpClient:
    def __init__(self) -> None:
        self.slot_events: list[list[str]] = []
        self.sent = threading.Event()

    def send_slots(self, slot_values: list[str]) -> None:
        self.slot_events.append(list(slot_values))
        self.sent.set()

    def send_arcade(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_dispatcher_coalesces_pending_slot_states() -> None:
    client = RecordingHttpClient()
    dispatcher = lector_rfid_4.EventDispatcher(client)
    dispatcher.publish_slots(["M", "", "", ""])
    dispatcher.publish_slots(["M", "A", "", ""])

    dispatcher.start()
    assert client.sent.wait(timeout=1)
    dispatcher.stop()

    assert client.slot_events == [["M", "A", "", ""]]


class FakeResponse:
    status = 200
    reason = "OK"

    def read(self) -> bytes:
        return b"{}"


class FakeConnection:
    def __init__(self) -> None:
        self.closed = False
        self.requests: list[tuple[str, str]] = []

    def request(self, method: str, path: str, **_kwargs: object) -> None:
        self.requests.append((method, path))

    def getresponse(self) -> FakeResponse:
        return FakeResponse()

    def close(self) -> None:
        self.closed = True


def test_http_client_refreshes_idle_keep_alive_connection(monkeypatch: object) -> None:
    client = lector_rfid_4.GameHttpClient("http://127.0.0.1:5000")
    stale_connection = FakeConnection()
    fresh_connection = FakeConnection()
    client._connection = stale_connection
    client._last_response_at = (
        time.monotonic() - lector_rfid_4.HTTP_KEEP_ALIVE_REFRESH_SECONDS - 1
    )
    monkeypatch.setattr(  # type: ignore[attr-defined]
        lector_rfid_4.http.client,
        "HTTPConnection",
        lambda *_args, **_kwargs: fresh_connection,
    )

    client.send_slots(["A", "", "", ""])

    assert stale_connection.closed is True
    assert fresh_connection.requests == [("POST", "/slots")]
