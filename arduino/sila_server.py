from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse


HOST = "0.0.0.0"
PORT = 5000

DELETE_COMMANDS = {"BORRAR", "DELETE", "BACKSPACE"}
RESET_COMMAND = "RESET"
RESET_ALL_COMMAND = "RESET_TODO"
ENTER_COMMAND = "ENTER"
NEXT_COMMAND = "SIGUIENTE"
PREVIOUS_COMMAND = "ANTERIOR"
KNOWN_COMMANDS = DELETE_COMMANDS | {
    RESET_COMMAND,
    RESET_ALL_COMMAND,
    ENTER_COMMAND,
    NEXT_COMMAND,
    PREVIOUS_COMMAND,
}

MISSIONS = [
    {
        "mission_id": "m001",
        "prompt": "Reconstruye la palabra MAMÁ",
        "target_blocks": ["MA", "MÁ"],
        "accepted_answers": ["MAMÁ", "MAMA"],
        "available_blocks": ["MA", "MÁ", "PA", "SA"],
    },
    {
        "mission_id": "m002",
        "prompt": "Reconstruye la palabra PAPÁ",
        "target_blocks": ["PA", "PÁ"],
        "accepted_answers": ["PAPÁ", "PAPA"],
        "available_blocks": ["PA", "PÁ", "MA", "SA"],
    },
    {
        "mission_id": "m003",
        "prompt": "Reconstruye la palabra CASA",
        "target_blocks": ["CA", "SA"],
        "accepted_answers": ["CASA"],
        "available_blocks": ["CA", "SA", "MA", "PA"],
    },
    {
        "mission_id": "m004",
        "prompt": "Reconstruye la palabra MESA",
        "target_blocks": ["ME", "SA"],
        "accepted_answers": ["MESA"],
        "available_blocks": ["ME", "SA", "CA", "PA"],
    },
    {
        "mission_id": "m005",
        "prompt": "Reconstruye la palabra BOTA",
        "target_blocks": ["B", "O", "T", "A"],
        "accepted_answers": ["BOTA"],
        "available_blocks": ["B", "O", "T", "A"],
    },
]

FEEDBACK_EMPTY = "Escanea un cubo para comenzar."
FEEDBACK_IN_PROGRESS = "Vas bien. Falta una parte."
FEEDBACK_SUCCESS_TEMPLATE = "Muy bien. Reconstruiste la palabra {target_text}."
FEEDBACK_SUCCESS = FEEDBACK_SUCCESS_TEMPLATE.format(target_text="MAMÁ")
FEEDBACK_TRY_AGAIN = "Casi. Prueba otra combinación."
FEEDBACK_KEEP_TRYING = "Sigue probando con los cubos."
FEEDBACK_WRONG_BLOCK = "Casi. Revisa el último cubo y prueba otra combinación."
FEEDBACK_NEXT_BLOCKED = "Primero completa esta palabra. Luego avanzamos."
FEEDBACK_DEMO_COMPLETE = "Muy bien. Completaste todas las misiones."
FEEDBACK_FIRST_MISSION = "Ya estás en la primera misión."


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("sillablocks")

app = FastAPI(title="SilaBlocks NFC Server")

current_blocks: list[str] = []
current_mission_index = 0
completed_mission_ids: set[str] = set()
last_input: str | None = None
last_received_input: str | None = None
last_ignored_input: str | None = None
last_action = "init"
game_status = "idle"
feedback = FEEDBACK_EMPTY
recent_inputs: list[dict[str, Any]] = []


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale_connections: list[WebSocket] = []
        message = json.dumps(payload, ensure_ascii=False)
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(websocket)


manager = ConnectionManager()


def normalize_input(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().upper()


def current_text() -> str:
    return "".join(current_blocks)


def current_mission() -> dict[str, Any]:
    return MISSIONS[current_mission_index]


def target_text() -> str:
    return current_mission()["accepted_answers"][0]


def mission_number() -> int:
    return current_mission_index + 1


def total_missions() -> int:
    return len(MISSIONS)


def is_last_mission() -> bool:
    return current_mission_index == len(MISSIONS) - 1


def is_prefix_of_target(blocks: list[str]) -> bool:
    target_blocks = current_mission()["target_blocks"]
    if len(blocks) > len(target_blocks):
        return False
    return blocks == target_blocks[: len(blocks)]


def is_exact_target_blocks(blocks: list[str]) -> bool:
    return blocks == current_mission()["target_blocks"]


def correct_prefix_count(blocks: list[str]) -> int:
    target_blocks = current_mission()["target_blocks"]
    count = 0
    for index, block in enumerate(blocks):
        if index >= len(target_blocks) or block != target_blocks[index]:
            break
        count += 1
    return count


def progress_percent() -> int:
    target_count = max(len(current_mission()["target_blocks"]), 1)
    return round((correct_prefix_count(current_blocks) / target_count) * 100)


def expected_next_block() -> str | None:
    count = correct_prefix_count(current_blocks)
    target_blocks = current_mission()["target_blocks"]
    if count < len(target_blocks):
        return target_blocks[count]
    return None


def remember_input(value: str, action: str, accepted: bool) -> None:
    recent_inputs.append(
        {
            "value": value,
            "action": action,
            "accepted": accepted,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    del recent_inputs[:-8]


def mark_current_mission_completed() -> None:
    completed_mission_ids.add(current_mission()["mission_id"])


def clear_current_buffer() -> None:
    current_blocks.clear()


def evaluate_game_state(validate_now: bool = False) -> None:
    global game_status, feedback

    if not current_blocks:
        game_status = "idle"
        feedback = FEEDBACK_EMPTY
        return

    if is_exact_target_blocks(current_blocks):
        mark_current_mission_completed()
        game_status = "success"
        feedback = FEEDBACK_SUCCESS_TEMPLATE.format(target_text=target_text())
        return

    if not is_prefix_of_target(current_blocks):
        game_status = "try_again"
        feedback = FEEDBACK_TRY_AGAIN if validate_now else FEEDBACK_WRONG_BLOCK
        return

    if validate_now:
        game_status = "try_again"
        feedback = FEEDBACK_TRY_AGAIN
        return

    game_status = "in_progress"
    feedback = FEEDBACK_IN_PROGRESS


def reset_game_state() -> None:
    global last_action, last_ignored_input
    completed_mission_ids.discard(current_mission()["mission_id"])
    clear_current_buffer()
    last_ignored_input = None
    last_action = "reset"
    evaluate_game_state()


def reset_all_game_state() -> None:
    global current_mission_index, last_action, last_ignored_input
    current_mission_index = 0
    completed_mission_ids.clear()
    clear_current_buffer()
    last_ignored_input = None
    last_action = "reset_all"
    evaluate_game_state()


def go_to_next_mission() -> bool:
    global current_mission_index, game_status, feedback, last_action, last_ignored_input

    if game_status != "success":
        last_action = "next_blocked"
        feedback = FEEDBACK_NEXT_BLOCKED
        return False

    mark_current_mission_completed()
    if is_last_mission():
        last_action = "demo_complete"
        game_status = "demo_complete"
        feedback = FEEDBACK_DEMO_COMPLETE
        return True

    current_mission_index += 1
    clear_current_buffer()
    last_ignored_input = None
    last_action = "next"
    evaluate_game_state()
    return True


def go_to_previous_mission() -> bool:
    global current_mission_index, game_status, feedback, last_action, last_ignored_input

    if current_mission_index == 0:
        last_action = "previous_blocked"
        feedback = FEEDBACK_FIRST_MISSION
        return False

    current_mission_index -= 1
    clear_current_buffer()
    last_ignored_input = None
    last_action = "previous"
    evaluate_game_state()
    return True


def build_state(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    text = current_text()
    correct_count = correct_prefix_count(current_blocks)
    mission = current_mission()
    state: dict[str, Any] = {
        "ok": True,
        "buffer": text,
        "texto": text,
        "bloques": list(current_blocks),
        "current_blocks": list(current_blocks),
        "current_text": text,
        "last_input": last_input,
        "ultimo_input": last_input,
        "last_received_input": last_received_input,
        "ultimo_recibido": last_received_input,
        "last_ignored_input": last_ignored_input,
        "ultimo_ignorado": last_ignored_input,
        "recent_inputs": list(recent_inputs),
        "accion": last_action,
        "action": last_action,
        "mission_id": mission["mission_id"],
        "mission_number": mission_number(),
        "total_missions": total_missions(),
        "completed_missions": len(completed_mission_ids),
        "completed_mission_ids": sorted(completed_mission_ids),
        "is_last_mission": is_last_mission(),
        "is_demo_complete": game_status == "demo_complete",
        "current_mission_index": current_mission_index,
        "prompt": mission["prompt"],
        "target_text": target_text(),
        "target_blocks": list(mission["target_blocks"]),
        "accepted_answers": list(mission["accepted_answers"]),
        "available_blocks": list(mission["available_blocks"]),
        "missions": [dict(item) for item in MISSIONS],
        "correct_prefix_count": correct_count,
        "target_block_count": len(mission["target_blocks"]),
        "progress_percent": 100 if game_status in {"success", "demo_complete"} else progress_percent(),
        "overall_progress_percent": round((len(completed_mission_ids) / total_missions()) * 100),
        "expected_next_block": expected_next_block(),
        "has_block_mismatch": bool(current_blocks) and not is_prefix_of_target(current_blocks),
        "status": game_status,
        "feedback": feedback,
        "mission": dict(mission),
    }
    if extra:
        state.update(extra)
    return state


async def broadcast_state() -> None:
    await manager.broadcast(build_state())


async def extract_nfc_value(request: Request, query_value: str | None) -> str:
    if query_value:
        return query_value

    body = await request.body()
    if not body:
        return ""

    raw_body = body.decode("utf-8", errors="ignore").strip()
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            return raw_body

        if isinstance(payload, dict):
            for key in ("letra", "valor", "value", "text", "payload"):
                value = payload.get(key)
                if isinstance(value, str):
                    return value
        if isinstance(payload, str):
            return payload

    return raw_body


async def handle_nfc_value(raw_value: str) -> JSONResponse:
    global last_action, last_input, last_received_input, last_ignored_input

    value = normalize_input(raw_value)
    if not value:
        return JSONResponse(
            status_code=400,
            content=build_state(
                {
                    "ok": False,
                    "error": "Parametro 'letra' vacio o ausente.",
                }
            ),
        )

    last_received_input = value
    accepted = True

    if value in DELETE_COMMANDS:
        if current_blocks:
            current_blocks.pop()
        last_action = "delete"
        last_input = value
        evaluate_game_state()
    elif value == RESET_COMMAND:
        last_input = value
        reset_game_state()
    elif value == RESET_ALL_COMMAND:
        last_input = value
        reset_all_game_state()
    elif value == ENTER_COMMAND:
        last_action = "validate"
        last_input = value
        evaluate_game_state(validate_now=True)
    elif value == NEXT_COMMAND:
        last_input = value
        accepted = go_to_next_mission()
    elif value == PREVIOUS_COMMAND:
        last_input = value
        accepted = go_to_previous_mission()
    elif game_status in {"success", "demo_complete"}:
        last_action = "ignored_after_success"
        last_ignored_input = value
        accepted = False
    else:
        current_blocks.append(value)
        last_action = "append"
        last_input = value
        evaluate_game_state()
    remember_input(value, last_action, accepted)

    logger.info(
        "NFC input=%s action=%s accepted=%s blocks=%s text=%s status=%s",
        value,
        last_action,
        accepted,
        current_blocks,
        current_text(),
        game_status,
    )
    state = build_state(
        {
            "letra": value,
            "valor": value,
            "command": value if value in KNOWN_COMMANDS else None,
            "accepted": accepted,
            "ignored": not accepted,
        }
    )
    await broadcast_state()
    return JSONResponse(content=state)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)

@app.get("/aldea", response_class=HTMLResponse)
async def aldea_view() -> HTMLResponse:
    return HTMLResponse(ALDEA_HTML)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "ok",
        "service": "sillablocks",
        "mission_id": current_mission()["mission_id"],
    }


@app.get("/buffer")
async def get_buffer() -> dict[str, Any]:
    return build_state()


@app.delete("/buffer")
async def delete_buffer() -> dict[str, Any]:
    global last_input, last_received_input

    last_input = RESET_COMMAND
    last_received_input = RESET_COMMAND
    reset_game_state()
    remember_input(RESET_COMMAND, last_action, True)
    await broadcast_state()
    return build_state({"letra": RESET_COMMAND, "valor": RESET_COMMAND})


@app.get("/nfc")
async def receive_nfc_get(letra: str | None = Query(default=None)) -> JSONResponse:
    return await handle_nfc_value(letra or "")


@app.post("/nfc")
async def receive_nfc_post(
    request: Request,
    letra: str | None = Query(default=None),
) -> JSONResponse:
    value = await extract_nfc_value(request, letra)
    return await handle_nfc_value(value)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    await websocket.send_text(json.dumps(build_state(), ensure_ascii=False))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SilaBlocks</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');
    /* Base */
    :root {
      color-scheme: dark;
      --ink: #2b160b;
      --muted: #6f431e;
      --deep: #120b16;
      --wood: #5b341c;
      --wood-dark: #28150c;
      --wood-light: #b77732;
      --gold: #f6c453;
      --gold-bright: #ffe8a3;
      --rune: #21c7ff;
      --purple: #39215f;
      --purple-bright: #6d3aa6;
      --green: #50d76c;
      --red: #8d221b;
      --blue: #075b88;
      --parchment: #d9b56e;
      --parchment-light: #f6dca2;
      --shadow: 0 26px 54px rgba(0, 0, 0, 0.54);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'Fredoka', Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 50% 28%, rgba(33, 199, 255, 0.18), transparent 25%),
        radial-gradient(circle at 20% 14%, rgba(246, 196, 83, 0.22), transparent 26%),
        radial-gradient(circle at 82% 18%, rgba(109, 58, 166, 0.20), transparent 26%),
        linear-gradient(180deg, #1a101c 0%, #211513 42%, #09070b 100%);
      overflow-x: hidden;
    }

    body::after {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      /* Partículas ligeramente más grandes y brillantes */
      background: transparent url('data:image/svg+xml;utf8,<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2.5" fill="%23ffe8a3" opacity="0.8"/><circle cx="200" cy="150" r="2" fill="%2321c7ff" opacity="0.7"/><circle cx="350" cy="300" r="3" fill="%23ffe8a3" opacity="0.8"/><circle cx="100" cy="350" r="1.5" fill="%2321c7ff" opacity="0.6"/></svg>') repeat;
      animation: floatParticles 60s linear infinite;
      z-index: 100; /* Trae el polvo mágico por encima de toda la interfaz */
    }

    button {
      font: inherit;
    }

    main {
      width: min(1320px, calc(100vw - 24px));
      margin: 0 auto;
      padding: 14px 0 20px;
    }

    h1, h2, h3, p {
      margin: 0;
    }

    /* Header */
    .topbar {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      padding: 14px 18px;
      border: 4px solid #8f5b28;
      border-radius: 8px;
      background:
        linear-gradient(180deg, rgba(255, 232, 163, 0.10), transparent 25%),
        linear-gradient(180deg, #5c351e, #2f190f 66%, #160b07);
      box-shadow: var(--shadow), inset 0 0 0 2px rgba(255, 232, 163, 0.16);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .brand h1 {
      position: relative;
      width: fit-content;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      color: #ffe8a3;
      font-size: clamp(42px, 6vw, 68px);
      font-weight: 900;
      line-height: 0.98;
      /* Efecto 3D mucho más profundo y contrastante */
      text-shadow: 
        0 2px 0 #e1a928,   /* Capa clara superior */
        0 4px 0 #b3731a,   /* Capa media */
        0 6px 0 #854d0a,   /* Capa oscura */
        0 8px 0 #522b03,   /* Capa muy oscura */
        0 10px 0 #2b1400,  /* Base profunda de la madera */
        0 15px 20px rgba(0, 0, 0, 0.8),    /* Sombra negra fuerte para despegarlo del fondo */
        0 0 35px rgba(255, 232, 163, 0.4); /* Resplandor mágico global */
      box-shadow: none;
      overflow: hidden;
    }

    /* Reflejo mágico que pasa sobre el título */
    .brand h1::after {
      content: "";
      position: absolute;
      top: 0; left: -150%;
      width: 50%; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
      transform: skewX(-25deg);
      animation: titleShine 5s infinite;
    }

    .subtitle {
      width: fit-content;
      padding: 8px 20px;
      border: 3px solid #5b341c;
      border-radius: 20px; /* Más redondo, estilo botón de videojuego */
      background: linear-gradient(180deg, #f6c453, #d7ad68 40%, #9d6a33);
      color: #2b160b;
      font-size: 22px;
      font-weight: 900;
      text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
      cursor: pointer;
      box-shadow: 0 6px 0 #4a260d, 0 8px 15px rgba(0, 0, 0, 0.3), inset 0 2px 0 rgba(255, 255, 255, 0.6);
      /* Animación de latido constante */
      animation: heartbeat 2s infinite ease-in-out;
      transition: box-shadow 0.1s;
    }

    .subtitle:active {
      animation: none; /* Pausa el latido al hacer clic */
      transform: translateY(4px);
      box-shadow: 0 2px 0 #4a260d, inset 0 2px 0 rgba(255, 255, 255, 0.6);
    }

    /* Layout */
    .layout {
      display: flex;
      flex-direction: column;
      align-items: stretch; /* Esto obliga a la tarjeta a usar todo el ancho horizontal */
      gap: 18px;
    }

    .mission-card,
    .side-card {
      position: relative;
      border: 4px solid #7b4b22;
      border-radius: 20px;
      background:
        linear-gradient(180deg, rgba(255, 238, 188, 0.34), rgba(255, 238, 188, 0.05) 14%, transparent 22%),
        linear-gradient(180deg, #d5a760, #c0914d 18%, #b37c3e 100%);
      box-shadow: var(--shadow), inset 0 0 0 2px rgba(255, 232, 163, 0.28);
    }

    .mission-card::before,
    .side-card::before {
      content: "";
      position: absolute;
      inset: 9px;
      pointer-events: none;
      border: 2px solid rgba(63, 37, 18, 0.26);
      border-radius: 12px;
    }

    .mission-card {
      display: grid;
      gap: 12px;
      padding: 16px 22px;
      overflow: hidden;
    }

    .mission-card::after {
      content: "";
      position: absolute;
      inset: auto -18% -44% -18%;
      height: 54%;
      pointer-events: none;
      background: radial-gradient(ellipse at center, rgba(33, 199, 255, 0.24), transparent 62%);
    }

    .mission-card > *,
    .side-card > * {
      position: relative;
      z-index: 1;
    }

    .prompt {
      color: #2b160b;
      font-size: clamp(28px, 4vw, 44px);
      font-weight: 900;
      line-height: 1.1;
      text-align: center;
      text-shadow: 0 2px 0 rgba(255, 238, 188, 0.32);
      padding: 0 10px;
    }

    /* Giant formed word panel */
    .formed-panel {
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 3px solid #6c4728;
      border-radius: 12px;
      background:
        linear-gradient(180deg, rgba(255, 238, 188, 0.14), rgba(54, 31, 22, 0.16)),
        #c99955;
      box-shadow: inset 0 0 24px rgba(43, 22, 11, 0.18), 0 8px 18px rgba(43, 22, 11, 0.24);
    }

    .formed {
      min-height: 180px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      border-radius: 12px;
      border: 4px solid #4b2b19;
      /* Fondo más oscuro y contrastante para que resalte la magia */
      background: radial-gradient(circle at center, rgba(33, 199, 255, 0.15), rgba(15, 12, 15, 0.95));
      color: #d6fbff;
      font-size: clamp(60px, 10vw, 120px);
      font-weight: 900;
      line-height: 1;
      overflow-wrap: anywhere;
      text-align: center;
      text-shadow: 0 4px 0 rgba(0, 0, 0, 0.6);
      /* Agregamos el palpitar del portal */
      animation: pulsePortal 3s infinite ease-in-out;
    }

    /* Controls */
    .side {
      display: grid;
      gap: 14px;
    }

    .side-card {
      display: grid;
      gap: 18px;
      padding: 24px;
      background:
        linear-gradient(180deg, rgba(255, 232, 163, 0.08), transparent 22%),
        linear-gradient(180deg, #4f2c19, #21120a);
    }

    .side-card h2 {
      color: #ffe8a3;
      font-size: 28px;
      text-align: center;
      line-height: 1.05;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.38);
    }

    .command-grid {
      display: flex;
      flex-direction: row;
      justify-content: space-between; /* Separa los botones usando todo el espacio disponible */
      gap: 16px;
      margin-top: 16px;
      width: 100%;
    }

    .command-grid .manual-button {
      flex: 1; /* Hace que crezcan igualitariamente */
      max-width: none; /* Quitamos el límite para que ocupen todo el espacio posible */
    }

    .manual-button {
      min-height: 50px;
      border: 4px solid #8b5b28;
      border-radius: 16px; /* Botones más circulares y amigables */
      background: linear-gradient(180deg, #e1bb73, #a56d2f 58%, #5b341c);
      color: #2b160b;
      font-size: 22px;
      font-weight: 900;
      cursor: pointer;
      text-shadow: 0 1px 0 rgba(255, 238, 188, 0.45);
      box-shadow: 0 6px 0 #3f2314, 0 8px 15px rgba(0, 0, 0, 0.3), inset 0 2px 0 rgba(255, 255, 255, 0.28);
      transition: transform 0.1s, box-shadow 0.1s, filter 0.2s; /* Transición suave para el clic */
    }

    .manual-button:hover {
      filter: brightness(1.12);
    }

    /* Efecto de hundimiento físico al hacer clic */
    .manual-button:active {
      transform: translateY(4px);
      box-shadow: 0 2px 0 #3f2314, inset 0 2px 0 rgba(255, 255, 255, 0.28);
    }

    .manual-button.command {
      min-height: 56px;
      border-color: #4b2b19;
      background: linear-gradient(180deg, #075b88, #063653);
      color: #d6fbff;
      font-size: 22px; /* Un poco más grande para leer mejor */
      box-shadow: 0 6px 0 #100b17, 0 8px 15px rgba(0, 0, 0, 0.3);
    }

    .manual-button.command:active {
      box-shadow: 0 2px 0 #100b17;
    }

    .manual-button.primary {
      border-color: #4b2b19;
      background: linear-gradient(180deg, #2f8f46, #155729);
      color: #f2fff0;
    }

    @media (max-width: 980px) {
      main {
        width: min(100vw - 20px, 780px);
        padding-top: 12px;
      }

      .topbar,
      .layout {
        grid-template-columns: 1fr;
      }
    }
    /* --- Animaciones Mágicas --- */
    @keyframes pulsePortal {
      0% { box-shadow: inset 0 0 20px rgba(33, 199, 255, 0.1); border-color: #4b2b19; }
      50% { box-shadow: inset 0 0 40px rgba(33, 199, 255, 0.4), 0 0 15px rgba(33, 199, 255, 0.2); border-color: #075b88; }
      100% { box-shadow: inset 0 0 20px rgba(33, 199, 255, 0.1); border-color: #4b2b19; }
    }

    @keyframes floatMagic {
      0% { transform: translateY(0px); filter: drop-shadow(0 0 5px rgba(214, 251, 255, 0.3)); }
      50% { transform: translateY(-8px); filter: drop-shadow(0 0 15px rgba(214, 251, 255, 0.8)); }
      100% { transform: translateY(0px); filter: drop-shadow(0 0 5px rgba(214, 251, 255, 0.3)); }
    }

    @keyframes blinkSoft {
      0%, 100% { opacity: 0.3; }
      50% { opacity: 0.8; }
    }

    .magic-word {
      display: inline-block;
      animation: floatMagic 3s infinite ease-in-out;
    }
    @keyframes floatParticles {
      from { background-position: 0 0; }
      to { background-position: -400px -400px; }
    }

    @keyframes titleShine {
      0%, 20% { left: -150%; }
      80%, 100% { left: 200%; }
    }

    @keyframes heartbeat {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.03); }
    }
  </style>
</head>
<body>
  <main>
    <header class="topbar">
      <div class="brand">
        <h1>SilaBlocks</h1>
        <a href="/aldea" class="subtitle" style="text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 8px;">
          🏰 El Mundo de las Palabras Perdidas
        </a>
      </div>
    </header>

    <div class="layout">
      <section class="mission-card" aria-label="Misión actual" style="width: 100%;">
        <div>
          <p class="prompt" style="font-size: clamp(20px, 3vw, 32px); margin-bottom: 4px;">Escucha la instrucción, e inserta el cubo asociado al sonido que escuchas</p>
          <p style="text-align: center; font-size: 18px; color: #5b341c; font-weight: bold; margin: 0;">(Por ejemplo: si se escucha "mmmm", poner M)</p>
        </div>
        
        <div class="formed-panel">
          <div class="formed" id="formed">-</div>
        </div>

        <div class="command-grid" id="commandButtons"></div>
      </section>
    </div>
  </main>

  <script>
    const commands = ["BORRAR", "SIGUIENTE", "ANTERIOR"];

    const ids = {
      formed: document.getElementById("formed"),
      commandButtons: document.getElementById("commandButtons")
    };

    function createButton(value, className) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = className;
      button.textContent = value;
      button.addEventListener("click", () => sendNfc(value));
      return button;
    }

    function renderCommandButtons() {
      ids.commandButtons.innerHTML = "";
      commands.forEach((value) => {
        const className = value === "SIGUIENTE" ? "manual-button command primary" : "manual-button command";
        ids.commandButtons.appendChild(createButton(value, className));
      });
    }

    async function sendNfc(value) {
      const response = await fetch(`/nfc?letra=${encodeURIComponent(value)}`);
      const payload = await response.json();
      render(payload);
    }

    function render(payload) {
      const word = payload.current_text || "";
      
      if (word === "") {
        // Estado vacío interactivo y titilante
        ids.formed.innerHTML = '<span style="animation: blinkSoft 1.5s infinite;">...</span>';
      } else {
        // Palabra insertada con efecto de flotar y brillar
        ids.formed.innerHTML = `<span class="magic-word">${word}</span>`;
      }
    }

    async function loadInitialState() {
      const response = await fetch("/buffer");
      const payload = await response.json();
      render(payload);
    }

    function connectSocket() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

      socket.addEventListener("message", (event) => {
        render(JSON.parse(event.data));
      });

      socket.addEventListener("close", () => {
        window.setTimeout(connectSocket, 1200);
      });
    }

    renderCommandButtons();
    loadInitialState();
    connectSocket();
  </script>
</body>
</html>
"""

ALDEA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mi Aldea - SilaBlocks</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      /* Degradado que va de cielo celeste a pasto verde */
      background: linear-gradient(180deg, #87CEEB 0%, #A2D9CE 30%, #7EC850 40%, #7EC850 100%);
      font-family: 'Fredoka', Arial, sans-serif; /* Usamos la misma fuente redondeada */
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 65px;
      overflow-x: hidden; /* Evita scroll horizontal por las nubes */
    }

    /* Patrón de pasto solo en la mitad inferior */
    body::before {
      content: "";
      position: fixed;
      inset: 40% 0 0 0;
      pointer-events: none;
      background-image: radial-gradient(#6ebd44 15%, transparent 16%), radial-gradient(#6ebd44 15%, transparent 16%);
      background-size: 60px 60px;
      background-position: 0 0, 30px 30px;
      z-index: -2;
    }

    /* Nubes animadas usando CSS puro (sin cargar imágenes externas) */
    body::after {
      content: "";
      position: fixed;
      top: 0; left: 0; right: 0; height: 30vh;
      pointer-events: none;
      background: transparent url('data:image/svg+xml;utf8,<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><path d="M 50 100 A 30 30 0 0 1 110 100 A 20 20 0 0 1 150 110 A 30 30 0 0 1 110 140 L 50 140 A 20 20 0 0 1 50 100" fill="white" opacity="0.6"/><path d="M 250 50 A 40 40 0 0 1 330 50 A 30 30 0 0 1 380 70 A 40 40 0 0 1 330 110 L 250 110 A 30 30 0 0 1 250 50" fill="white" opacity="0.4"/></svg>') repeat-x;
      animation: floatClouds 120s linear infinite;
      z-index: -1;
    }

    @keyframes floatClouds {
      from { background-position: 0 0; }
      to { background-position: 800px 0; }
    }

    /* Botón de volver arriba a la izquierda */
    .back-btn {
      position: absolute;
      top: 20px;
      left: 20px;
      padding: 12px 24px;
      background: #d94c3a;
      color: white;
      font-size: 18px;
      font-weight: 900;
      text-decoration: none;
      border: 4px solid #8d221b;
      border-radius: 12px;
      box-shadow: 0 6px 0 #5c1410;
      transition: transform 0.1s, box-shadow 0.1s;
    }

    .back-btn:active {
      transform: translateY(6px);
      box-shadow: 0 0 0 #5c1410;
    }

    /* Contador de tokens arriba a la derecha */
    .token-display {
      position: absolute;
      top: 20px;
      right: 20px;
      background: #f6c453;
      color: #2b160b;
      padding: 12px 24px;
      font-size: 24px;
      font-weight: 900;
      border: 4px solid #b77732;
      border-radius: 12px;
      box-shadow: 0 6px 0 #a56d2f;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h1 {
      position: relative;
      color: #ffe8a3;
      font-size: clamp(32px, 5vw, 50px); /* Título un poco más compacto */
      font-weight: 900;
      line-height: 0.98;
      margin-bottom: 5px; /* Eliminamos casi todo el margen de abajo */
      text-align: center;
      text-shadow: 
        0 2px 0 #e1a928, 0 4px 0 #b3731a, 0 6px 0 #854d0a,
        0 8px 0 #522b03, 0 10px 0 #2b1400,
        0 15px 20px rgba(0, 0, 0, 0.6), 0 0 35px rgba(255, 232, 163, 0.4);
    }

    /* Brillo mágico pasando sobre el título */
    h1::after {
      content: "";
      position: absolute;
      top: 0; left: -150%;
      width: 50%; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
      transform: skewX(-25deg);
      animation: titleShine 5s infinite;
    }
    
    @keyframes titleShine {
      0%, 20% { left: -150%; }
      80%, 100% { left: 200%; }
    }

    .yard {
      display: flex;
      gap: 80px;
      margin-top: 15px;
      padding: 35px 60px 25px 60px;
      background-color: #e3bc84;
      /* Textura de tierrita (puntitos semi-transparentes) */
      background-image: 
        radial-gradient(rgba(139, 91, 40, 0.15) 15%, transparent 16%), 
        radial-gradient(rgba(139, 91, 40, 0.15) 15%, transparent 16%);
      background-size: 20px 20px;
      background-position: 0 0, 10px 10px;
      border-radius: 30px;
      border: 8px solid #8b5b28;
      box-shadow: 
        inset 0 0 30px rgba(139, 91, 40, 0.4),
        0 15px 0 #5a9e33,
        0 20px 20px rgba(0,0,0,0.3);
    }

    .house-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      position: relative; /* Para anclar la sombra */
    }

    /* Sombra de base en el piso */
    .house-container::after {
      content: '';
      position: absolute;
      bottom: 60px; /* Ajustado para quedar bajo la casa */
      width: 160px;
      height: 30px;
      background: rgba(139, 91, 40, 0.5); /* Sombra color tierra oscura */
      border-radius: 50%;
      z-index: 0;
      filter: blur(4px);
    }

    .house {
      width: 140px;
      height: 120px;
      background-color: #f4d3a1; /* Madera un poco más clara para contrastar */
      border: 6px solid #8b5b28;
      border-radius: 8px;
      position: relative;
      transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      z-index: 1; /* Encima de la sombra */
      transform-origin: bottom center;
    }

    /* Techo (Triángulo) */
    .house::before { 
      content: '';
      position: absolute;
      top: -66px; 
      left: 50%;
      transform: translateX(-50%); 
      border-left: 95px solid transparent; /* Más ancho que la casa */
      border-right: 95px solid transparent;
      border-bottom: 60px solid #d94c3a;
      z-index: 4;
      /* Alero del techo */
      filter: drop-shadow(0px 8px 0px #8d221b); 
    }

    /* Puerta */
    .house::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 40px;
      height: 60px;
      background-color: #633a18;
      border-radius: 20px 20px 0 0;
      border: 4px solid #4a260d; /* Marco de la puerta */
      border-bottom: none;
    }

    .level-badge {
      background: #f6c453;
      color: #2b160b;
      padding: 8px 16px;
      border-radius: 20px;
      font-weight: 900;
      font-size: 20px;
      border: 3px solid #b77732;
      box-shadow: 0 4px 0 #a56d2f;
      z-index: 10;
    }

    .upgrade-btn {
      padding: 12px 24px;
      background: #21c7ff;
      color: #073653;
      font-size: 18px;
      font-weight: 900;
      border: 4px solid #075b88;
      border-radius: 16px; /* Más redondo */
      cursor: pointer;
      box-shadow: 0 6px 0 #063653, 0 8px 15px rgba(0,0,0,0.3), inset 0 2px 0 rgba(255,255,255,0.4);
      transition: transform 0.1s, box-shadow 0.1s, filter 0.2s;
      z-index: 2; /* Sobre la sombra */
    }

    .upgrade-btn:active {
      transform: translateY(4px);
      box-shadow: 0 2px 0 #063653, inset 0 2px 0 rgba(255,255,255,0.4);
    }

    /* Estado visual cuando no hay tokens */
    .upgrade-btn.disabled {
      filter: grayscale(100%);
      cursor: not-allowed;
    }

    /* Detalles decorativos de las casas */
    .window {
      position: absolute;
      top: 25px;
      width: 28px;
      height: 28px;
      background: #d6fbff;
      border: 4px solid #633a18;
      border-radius: 4px;
      opacity: 0; /* Oculto por defecto */
      transition: opacity 0.5s ease-in;
      z-index: 2;
    }
    
    /* Forma de cruz en las ventanas */
    .window::before {
      content: ''; position: absolute;
      top: 50%; left: 0; right: 0; height: 4px; background: #633a18; transform: translateY(-50%);
    }
    .window::after {
      content: ''; position: absolute;
      left: 50%; top: 0; bottom: 0; width: 4px; background: #633a18; transform: translateX(-50%);
    }
    
    .window-left { left: 12px; }
    .window-right { right: 12px; }

    .chimney {
      position: absolute;
      top: -75px; /* La bajamos para que toque el techo */
      right: 18px; /* Ajuste horizontal fino */
      width: 22px;
      height: 55px; /* Más alta para que se hunda bien atrás del triángulo rojo */
      background: #c2593a;
      border: 4px solid #8d221b;
      opacity: 0; 
      transition: opacity 0.5s ease-in;
      z-index: -1; 
    }

    .bush {
      position: absolute;
      bottom: -4px;
      left: -20px;
      width: 45px;
      height: 35px;
      background: #50d76c;
      border: 4px solid #226b36;
      border-radius: 20px 20px 0 0;
      opacity: 0; /* Oculto por defecto */
      transition: opacity 0.5s ease-in;
      z-index: 3;
    }

    /* Sistema de niveles: hace aparecer los elementos progresivamente */
    .lvl-2 .window-left { opacity: 1; }
    .lvl-3 .window-right { opacity: 1; }
    .lvl-4 .chimney { opacity: 1; }
    .lvl-5 .bush { opacity: 1; }

    /* Sol Giratorio y Rayos */
    .sun {
      position: absolute;
      top: 40px;
      left: 12vw; /* Lo ubicamos a la izquierda */
      width: 80px;
      height: 80px;
      background: #f6c453;
      border-radius: 50%;
      box-shadow: 0 0 40px #f6c453, 0 0 80px #f6c453; /* Resplandor */
      z-index: -2; /* Para que quede detrás de las nubes */
      display: flex;
      align-items: center;
      justify-content: center;
      animation: spinSun 40s linear infinite; /* Rota muy lentamente */
    }

    .sun::before {
      content: '';
      position: absolute;
      width: 130px;
      height: 130px;
      border: 4px dashed rgba(246, 196, 83, 0.6); /* Rayos del sol */
      border-radius: 50%;
    }

    @keyframes spinSun {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>

  <!-- El nuevo Sol Animado -->
  <div class="sun"></div>

  <a href="/" class="back-btn">⬅ Volver a SilaBlocks</a>
  
  <div class="token-display">
    🪙 Tokens: <span id="tokenCount">5</span>
  </div>

  <h1>La Aldea Restaurada</h1>
  
  <div class="yard">
    <div class="house-container">
      <div class="level-badge" id="badge1">Nivel 1</div>
      <div class="house lvl-1" id="house1">
        <div class="chimney"></div>
        <div class="window window-left"></div>
        <div class="window window-right"></div>
        <div class="bush"></div>
      </div>
      <button class="upgrade-btn" id="btn1" onclick="upgradeHouse(1)">✨ Mejorar (1)</button>
    </div>

    <div class="house-container">
      <div class="level-badge" id="badge2">Nivel 1</div>
      <div class="house lvl-1" id="house2">
        <div class="chimney"></div>
        <div class="window window-left"></div>
        <div class="window window-right"></div>
        <div class="bush"></div>
      </div>
      <button class="upgrade-btn" id="btn2" onclick="upgradeHouse(2)">✨ Mejorar (1)</button>
    </div>
  </div>

  <script>
    let levels = { 1: 1, 2: 1 };
    let tokens = 5; // Comenzamos con 5 tokens

    function updateButtonsState() {
      // Si no hay tokens, ponemos los botones en gris
      if (tokens <= 0) {
        document.getElementById('btn1').classList.add('disabled');
        document.getElementById('btn2').classList.add('disabled');
      }
    }

    function upgradeHouse(id) {
      if (tokens >= 1) {
        // Restamos el token
        tokens--;
        document.getElementById('tokenCount').innerText = tokens;
        
        // Guardamos el nivel anterior para la animación
        let prevLevel = levels[id];
        
        // Subimos el nivel de la casa
        levels[id]++;
        document.getElementById('badge' + id).innerText = 'Nivel ' + levels[id];
        
        let house = document.getElementById('house' + id);
        let prevScale = 1 + (prevLevel * 0.05);
        let newScale = 1 + (levels[id] * 0.05); 
        
        // Animación de "Salto Mágico" usando la API de animaciones nativa
        house.animate([
          { transform: `scale(${prevScale}) scaleY(0.85) scaleX(1.1)` }, // Se aplasta para tomar impulso
          { transform: `scale(${newScale}) scaleY(1.1) scaleX(0.95)`, offset: 0.5 }, // Salta y se estira hacia arriba
          { transform: `scale(${newScale}) scaleY(1) scaleX(1)` } // Cae suavemente en su nuevo tamaño
        ], { 
          duration: 400, 
          easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)' 
        });

        // Fijamos el tamaño final para cuando termine la animación
        house.style.transform = `scale(${newScale})`;

        // Agregamos la clase del nivel para que aparezcan chimeneas, ventanas, etc.
        house.classList.add('lvl-' + levels[id]);

        // Verificamos si debemos desactivar los botones
        updateButtonsState();
      } else {
        alert("¡Oh no! No tienes suficientes tokens. Vuelve a SilaBlocks para jugar y ganar más.");
      }
    }
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)