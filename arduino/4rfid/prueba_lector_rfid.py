from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


DEFAULT_BAUD_RATE = 115200
DEFAULT_PORT = "COM6"
DEFAULT_MAP_PATH = Path(__file__).resolve().parents[1] / "rfid_uid_map.json"
NUM_SLOTS = 4


def normalize_uid(value: str) -> str:
    return value.strip().replace(" ", "").replace(":", "").replace("-", "").upper()


def load_uid_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

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


def print_slot_event(line: str, uid_map: dict[str, str]) -> None:
    if line == "BUTTON,ENTER":
        print("Boton presionado")
        return

    parsed = parse_slot_line(line)
    if parsed is None:
        print(line)
        return

    slot_index, uid = parsed
    if not uid:
        print(f"Lector {slot_index + 1} sin tag")
        return

    print(f"Lector {slot_index + 1} detecto tag! UID: {uid}")
    value = uid_map.get(uid)
    if value:
        print(f"Tag mapeado como: {value}")
    else:
        print(f"TAG NO MAPEADO: {uid}")


def run_serial_test(args: argparse.Namespace, uid_map: dict[str, str]) -> None:
    import serial

    print(f"Probando RFID desde {args.port} a {args.baud} baudios")
    print(f"Mapa RFID local: {args.map}")
    print("Este script solo muestra mensajes por consola. No se conecta al juego.")

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
                print_slot_event(raw_line, uid_map)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prueba local de 4 RFID. No envia nada al juego."
    )
    parser.add_argument(
        "port",
        nargs="?",
        default=DEFAULT_PORT,
        help="Puerto Serial del ESP32/Arduino, por ejemplo COM6",
    )
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD_RATE)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP_PATH)
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
        for line in args.simulate:
            print_slot_event(line, uid_map)
        return

    run_serial_test(args, uid_map)


if __name__ == "__main__":
    main()
