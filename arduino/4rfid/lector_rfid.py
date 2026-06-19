from __future__ import annotations

import argparse
import http.client
import json
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DEFAULT_BAUD_RATE = 115200
DEFAULT_PORT = "COM6"
# 127.0.0.1 avoids DNS/IPv6 fallback delays seen with localhost on Windows.
DEFAULT_SERVER_URL = "http://127.0.0.1:5000"
DEFAULT_MAP_PATH = Path(__file__).resolve().parents[1] / "rfid_uid_map.json"
NUM_SLOTS = 4
SERIAL_TIMEOUT_SECONDS = 0.05
RECONNECT_DELAY_SECONDS = 0.5
HTTP_TIMEOUT_SECONDS = 0.5
HTTP_KEEP_ALIVE_REFRESH_SECONDS = 4.0


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


class GameHttpClient:
    """Persistent low-latency HTTP connection to the local game server."""

    def __init__(self, server_url: str, timeout: float = HTTP_TIMEOUT_SECONDS) -> None:
        parsed = urlsplit(server_url)
        if parsed.scheme != "http" or not parsed.hostname:
            raise ValueError("--server-url debe ser una URL http valida")

        self.host = parsed.hostname
        self.port = parsed.port or 80
        self.base_path = parsed.path.rstrip("/")
        self.timeout = timeout
        self._connection: http.client.HTTPConnection | None = None
        self._last_response_at = 0.0

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        self._last_response_at = 0.0

    def _request(self, method: str, path: str, payload: dict[str, str] | None = None) -> None:
        # Uvicorn closes idle keep-alive connections after 5 seconds by default.
        # Refresh first so Windows never has to reuse a socket left in CLOSE_WAIT.
        if (
            self._connection is not None
            and time.monotonic() - self._last_response_at >= HTTP_KEEP_ALIVE_REFRESH_SECONDS
        ):
            self.close()

        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Connection": "keep-alive"}
        if body is not None:
            headers["Content-Type"] = "application/json"

        if self._connection is None:
            self._connection = http.client.HTTPConnection(
                self.host,
                self.port,
                timeout=self.timeout,
            )

        try:
            self._connection.request(method, f"{self.base_path}{path}", body=body, headers=headers)
            response = self._connection.getresponse()
            response.read()
            if not 200 <= response.status < 300:
                raise OSError(f"HTTP {response.status} {response.reason}")
            self._last_response_at = time.monotonic()
        except (OSError, http.client.HTTPException):
            self.close()
            raise

    def send_slots(self, slot_values: list[str]) -> None:
        payload = {f"s{index}": value for index, value in enumerate(slot_values)}
        for attempt in range(2):
            try:
                self._request("POST", "/slots", payload)
                return
            except (OSError, http.client.HTTPException):
                if attempt == 1:
                    raise
                # /slots replaces the complete state, so one immediate retry is safe.
                self.close()

    def send_arcade(self) -> None:
        self._request("GET", "/arcade")


class EventDispatcher:
    """Send network events off the Serial thread and coalesce stale slot states."""

    def __init__(self, client: GameHttpClient) -> None:
        self.client = client
        self._events: queue.Queue[str] = queue.Queue()
        self._lock = threading.Lock()
        self._latest_slots: list[str] | None = None
        self._slots_queued = False
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run, name="rfid-http", daemon=True)
        self._last_error_at = 0.0

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stopped.set()
        self._events.put("stop")
        self._thread.join(timeout=1)
        self.client.close()

    def publish_slots(self, slot_values: list[str]) -> None:
        with self._lock:
            self._latest_slots = list(slot_values)
            if self._slots_queued:
                return
            self._slots_queued = True
        self._events.put("slots")

    def publish_arcade(self) -> None:
        self._events.put("arcade")

    def _take_latest_slots(self) -> list[str] | None:
        with self._lock:
            slots = self._latest_slots
            self._latest_slots = None
            self._slots_queued = False
            return slots

    def _restore_slots_after_failure(self, slots: list[str]) -> None:
        with self._lock:
            if self._latest_slots is None:
                self._latest_slots = slots
            if self._slots_queued:
                return
            self._slots_queued = True
        self._events.put("slots")

    def _log_network_error(self, exc: BaseException) -> None:
        now = time.monotonic()
        if now - self._last_error_at >= 2:
            print(f"Servidor no disponible; reintentando sin detener RFID: {exc}", flush=True)
            self._last_error_at = now

    def _run(self) -> None:
        while not self._stopped.is_set():
            event = self._events.get()
            if event == "stop":
                return

            slots: list[str] | None = None
            try:
                if event == "arcade":
                    self.client.send_arcade()
                elif event == "slots":
                    slots = self._take_latest_slots()
                    if slots is not None:
                        self.client.send_slots(slots)
            except (OSError, http.client.HTTPException) as exc:
                self._log_network_error(exc)
                if event == "arcade":
                    self._events.put("arcade")
                elif slots is not None:
                    self._restore_slots_after_failure(slots)
                self._stopped.wait(RECONNECT_DELAY_SECONDS)


def send_slots(server_url: str, slot_values: list[str]) -> bool:
    client = GameHttpClient(server_url)
    try:
        client.send_slots(slot_values)
    except OSError as exc:
        print(f"No se pudo enviar /slots al juego ({exc}). ¿Está levantado sila_server.py?")
        return False
    finally:
        client.close()
    return True


def send_arcade(server_url: str) -> bool:
    client = GameHttpClient(server_url)
    try:
        client.send_arcade()
    except OSError as exc:
        print(f"No se pudo enviar /arcade al juego ({exc}). ¿Está levantado sila_server.py?")
        return False
    finally:
        client.close()
    return True


def process_line(
    line: str,
    slot_uids: list[str],
    uid_map: dict[str, str],
    server_url: str,
    dry_run: bool,
    dispatcher: EventDispatcher | None = None,
) -> bool:
    if line == "BUTTON,ENTER":
        print("Boton presionado")
        if dry_run:
            print("Boton -> ENTER (sin enviar)")
        elif dispatcher is not None:
            dispatcher.publish_arcade()
            print("Boton -> ENTER")
        else:
            sent = send_arcade(server_url)
            print("Boton -> ENTER" if sent else "Boton -> ENTER pendiente")
        return True

    parsed = parse_slot_line(line)
    if parsed is None:
        print(line)
        return False

    slot_index, uid = parsed
    if slot_uids[slot_index] == uid:
        return True

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
    elif dispatcher is not None:
        dispatcher.publish_slots(slot_values)
        print(f"Espacios -> {slot_values}")
    else:
        sent = send_slots(server_url, slot_values)
        print(f"Espacios -> {slot_values}" if sent else f"Espacios pendientes -> {slot_values}")
    return True


def run_serial_bridge(args: argparse.Namespace, uid_map: dict[str, str]) -> None:
    import serial

    print(f"Leyendo 4 RFID desde {args.port} a {args.baud} baudios")
    print(f"Enviando espacios al juego básico en {args.server_url}/slots")
    print(f"Mapa RFID: {args.map}")

    dispatcher = EventDispatcher(GameHttpClient(args.server_url))
    dispatcher.start()

    try:
        while True:
            slot_uids = ["", "", "", ""]
            try:
                with serial.Serial(
                    args.port,
                    args.baud,
                    timeout=SERIAL_TIMEOUT_SECONDS,
                ) as device:
                    print(f"Puerto {args.port} conectado", flush=True)
                    time.sleep(1.5)
                    while True:
                        raw_line = device.readline().decode("utf-8", errors="ignore").strip()
                        if raw_line:
                            process_line(
                                raw_line,
                                slot_uids,
                                uid_map,
                                args.server_url,
                                args.dry_run,
                                dispatcher,
                            )
            except (serial.SerialException, OSError) as exc:
                dispatcher.publish_slots(["", "", "", ""])
                print(f"Puerto {args.port} no disponible: {exc}", flush=True)
                print("Reintentando automáticamente...", flush=True)
                time.sleep(RECONNECT_DELAY_SECONDS)
    finally:
        dispatcher.stop()


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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
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
