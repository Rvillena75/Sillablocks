from __future__ import annotations

import importlib.util
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
