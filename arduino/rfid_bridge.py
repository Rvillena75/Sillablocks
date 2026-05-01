from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_BAUD_RATE = 9600
DEFAULT_SERVER_URL = "http://localhost:5000/nfc"
DEFAULT_MAP_PATH = Path(__file__).with_name("rfid_uid_map.json")
READY_LINE = "SILABLOCKS_RFID_READY"


def normalize_uid(value: str) -> str:
    return value.strip().replace(" ", "").replace(":", "").replace("-", "").upper()


def load_uid_map(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as file:
        raw_map: dict[str, Any] = json.load(file)

    uid_map: dict[str, str] = {}
    for raw_uid, raw_value in raw_map.items():
        uid = normalize_uid(str(raw_uid))
        value = str(raw_value).strip().upper()
        if uid and value and not uid.startswith("REEMPLAZA_UID"):
            uid_map[uid] = value
    return uid_map


def send_to_server(server_url: str, value: str) -> None:
    query = urlencode({"letra": value})
    with urlopen(f"{server_url}?{query}", timeout=3) as response:
        response.read()


def process_uid(uid: str, uid_map: dict[str, str], server_url: str, dry_run: bool) -> bool:
    normalized_uid = normalize_uid(uid)
    if not normalized_uid or normalized_uid == READY_LINE:
        return False

    value = uid_map.get(normalized_uid)
    if value is None:
        print(f"UID no registrado: {normalized_uid}")
        return False

    if dry_run:
        print(f"{normalized_uid} -> {value} (sin enviar)")
        return True

    send_to_server(server_url, value)
    print(f"{normalized_uid} -> {value}")
    return True


def run_serial_bridge(args: argparse.Namespace, uid_map: dict[str, str]) -> None:
    import serial

    print(f"Leyendo RFID desde {args.port} a {args.baud} baudios")
    print(f"Enviando eventos a {args.server_url}")

    with serial.Serial(args.port, args.baud, timeout=1) as device:
        time.sleep(2)
        while True:
            raw_line = device.readline().decode("utf-8", errors="ignore").strip()
            if raw_line:
                process_uid(raw_line, uid_map, args.server_url, args.dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Puente Serial RFID -> servidor SilaBlocks /nfc?letra=..."
    )
    parser.add_argument("port", nargs="?", help="Puerto Serial del Arduino, por ejemplo COM3")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD_RATE)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP_PATH)
    parser.add_argument("--dry-run", action="store_true", help="No enviar al servidor")
    parser.add_argument(
        "--simulate",
        metavar="UID",
        help="Procesa un UID sin usar Arduino, útil para probar el mapeo",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    uid_map = load_uid_map(args.map)

    if args.simulate:
        process_uid(args.simulate, uid_map, args.server_url, args.dry_run)
        return

    if not args.port:
        raise SystemExit("Indica el puerto del Arduino, por ejemplo: python arduino\\rfid_bridge.py COM3")

    run_serial_bridge(args, uid_map)


if __name__ == "__main__":
    main()
