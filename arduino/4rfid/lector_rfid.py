from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_BAUD_RATE = 115200
DEFAULT_PORT = "COM6"
DEFAULT_SERVER_URL = "http://localhost:5000"
DEFAULT_MAP_PATH = Path(__file__).resolve().parents[1] / "rfid_uid_map.json"
NUM_SLOTS = 4


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


def parse_slot_line(line: str) -> tuple[int, str] | None:
    """Parse lines emitted by the 4-reader sketch: SLOT,<0-3>,<UID-or-empty>."""
    parts = [part.strip() for part in line.split(",", 2)]
    if len(parts) != 3 or parts[0] != "SLOT":
        return None

    try:
        slot_index = int(parts[1])
    except ValueError:
        return None

    if slot_index < 0 or slot_index >= NUM_SLOTS:
        return None

    return slot_index, normalize_uid(parts[2])


def slot_values_from_uids(slot_uids: list[str], uid_map: dict[str, str]) -> list[str]:
    values: list[str] = []
    for uid in slot_uids:
        values.append(uid_map.get(uid, "") if uid else "")
    return values


def send_slots(server_url: str, slot_values: list[str]) -> bool:
    query = urlencode({f"s{index}": value for index, value in enumerate(slot_values)})
    try:
        with urlopen(f"{server_url.rstrip('/')}/slots?{query}", timeout=3) as response:
            response.read()
    except OSError as exc:
        print(f"No se pudo enviar /slots al juego ({exc}). ¿Está levantado sila_server.py?")
        return False
    return True


def send_arcade(server_url: str) -> bool:
    try:
        with urlopen(f"{server_url.rstrip('/')}/arcade", timeout=3) as response:
            response.read()
    except OSError as exc:
        print(f"No se pudo enviar /arcade al juego ({exc}). ¿Está levantado sila_server.py?")
        return False
    return True


def process_line(
    line: str,
    slot_uids: list[str],
    uid_map: dict[str, str],
    server_url: str,
    dry_run: bool,
) -> bool:
    if line == "BUTTON,ENTER":
        print("Boton presionado")
        if dry_run:
            print("Boton -> ENTER (sin enviar)")
        else:
            sent = send_arcade(server_url)
            print("Boton -> ENTER" if sent else "Boton -> ENTER pendiente")
        return True

    parsed = parse_slot_line(line)
    if parsed is None:
        print(line)
        return False

    slot_index, uid = parsed
    slot_uids[slot_index] = uid
    slot_values = slot_values_from_uids(slot_uids, uid_map)

    if uid:
        print(f"Lector {slot_index + 1} detecto tag! UID: {uid}")
        if uid in uid_map:
            print(f"Tag mapeado como: {uid_map[uid]}")
        else:
            print(f"TAG NO MAPEADO: {uid}")
    else:
        print(f"Lector {slot_index + 1} sin tag")

    if dry_run:
        print(f"Espacios -> {slot_values} (sin enviar)")
    else:
        sent = send_slots(server_url, slot_values)
        print(f"Espacios -> {slot_values}" if sent else f"Espacios pendientes -> {slot_values}")
    return True


def run_serial_bridge(args: argparse.Namespace, uid_map: dict[str, str]) -> None:
    import serial

    slot_uids = ["", "", "", ""]
    print(f"Leyendo 4 RFID desde {args.port} a {args.baud} baudios")
    print(f"Enviando espacios al juego básico en {args.server_url}/slots")
    print(f"Mapa RFID: {args.map}")

    with serial.Serial(args.port, args.baud, timeout=1) as device:
        time.sleep(2)
        while True:
            try:
                raw_line = device.readline().decode("utf-8", errors="ignore").strip()
            except serial.SerialException as exc:
                print(f"Error leyendo {args.port}: {exc}")
                print("Cierra el Monitor Serial/Arduino IDE si está usando el puerto y vuelve a intentar.")
                time.sleep(1)
                continue

            if raw_line:
                process_line(raw_line, slot_uids, uid_map, args.server_url, args.dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Puente Serial 4 RFID -> juego basico SilaBlocks /slots"
    )
    parser.add_argument(
        "port",
        nargs="?",
        default=DEFAULT_PORT,
        help="Puerto Serial del ESP32/Arduino, por ejemplo COM6",
    )
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD_RATE)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP_PATH)
    parser.add_argument("--dry-run", action="store_true", help="No enviar al servidor")
    parser.add_argument(
        "--simulate",
        metavar="LINEA",
        action="append",
        help="Procesa una linea Serial sin abrir el puerto, por ejemplo SLOT,0,DAE9C103",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    uid_map = load_uid_map(args.map)

    if args.simulate:
        slot_uids = ["", "", "", ""]
        for line in args.simulate:
            process_line(line, slot_uids, uid_map, args.server_url, args.dry_run)
        return

    run_serial_bridge(args, uid_map)


if __name__ == "__main__":
    main()
