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
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 50% 28%, rgba(33, 199, 255, 0.18), transparent 25%),
        radial-gradient(circle at 20% 14%, rgba(246, 196, 83, 0.22), transparent 26%),
        radial-gradient(circle at 82% 18%, rgba(109, 58, 166, 0.20), transparent 26%),
        linear-gradient(180deg, #1a101c 0%, #211513 42%, #09070b 100%);
      overflow-x: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(90deg, transparent 0 49%, rgba(246, 196, 83, 0.06) 49% 51%, transparent 52%),
        linear-gradient(0deg, transparent 0 49%, rgba(33, 199, 255, 0.05) 49% 51%, transparent 52%);
      background-size: 170px 170px;
      mask-image: radial-gradient(circle at center, black, transparent 80%);
    }

    button {
      font: inherit;
    }

    main {
      width: min(1320px, calc(100vw - 24px));
      margin: 0 auto;
      padding: 14px 0 20px;
    }

    h1,
    h2,
    h3,
    p {
      margin: 0;
    }

    .label {
      width: fit-content;
      margin: 0 auto;
      padding: 7px 20px 8px;
      border: 2px solid #9f6a2d;
      border-radius: 8px;
      background: linear-gradient(180deg, var(--purple-bright), var(--purple) 65%, #211038);
      color: var(--gold-bright);
      font-size: 13px;
      font-weight: 900;
      letter-spacing: 0;
      text-transform: uppercase;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.36);
      box-shadow: 0 4px 0 #241224, 0 0 14px rgba(246, 196, 83, 0.18);
    }

    /* Header */
    .topbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 18px;
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
      display: grid;
      gap: 4px;
    }

    .brand h1 {
      width: fit-content;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      color: #ffe8a3;
      font-size: clamp(48px, 6vw, 82px);
      font-weight: 900;
      line-height: 0.98;
      text-shadow: 0 4px 0 #4a260d, 0 0 22px rgba(255, 232, 163, 0.55);
      box-shadow: none;
    }

    .subtitle {
      width: fit-content;
      padding: 7px 22px;
      border: 2px solid #a56d2f;
      border-radius: 8px;
      background: linear-gradient(180deg, #d7ad68, #9d6a33);
      color: #2b160b;
      font-size: clamp(17px, 2.3vw, 28px);
      font-weight: 900;
      text-shadow: 0 1px 0 rgba(255, 255, 255, 0.32);
    }

    .connection {
      min-width: 142px;
      padding: 12px 15px;
      border: 3px solid #5b341c;
      border-radius: 8px;
      background:
        linear-gradient(180deg, rgba(255, 232, 163, 0.12), transparent 30%),
        linear-gradient(180deg, #4b2a18, #1c0e08);
      color: #7cff81;
      font-size: 15px;
      font-weight: 900;
      text-align: center;
      box-shadow: 0 0 18px rgba(80, 215, 108, 0.20), inset 0 0 12px rgba(0, 0, 0, 0.28);
    }

    /* Layout */
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(310px, 360px);
      gap: 18px;
      align-items: start;
    }

    .mission-card,
    .side-card {
      position: relative;
      border: 4px solid #7b4b22;
      border-radius: 8px;
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
      border-radius: 6px;
    }

    .mission-card {
      display: grid;
      gap: 14px;
      padding: 20px 22px;
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

    .mission-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 14px;
      align-items: start;
    }

    .mission-pill {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      min-height: 34px;
      margin: 0 auto;
      padding: 8px 58px;
      border: 3px solid #9f6a2d;
      border-radius: 8px;
      background: linear-gradient(180deg, #56307d, #2b1746 68%, #160b24);
      color: #ffe8a3;
      font-size: 16px;
      font-weight: 900;
      box-shadow: 0 5px 0 #231224, 0 0 16px rgba(246, 196, 83, 0.22);
    }

    .prompt {
      margin-top: 8px;
      color: #2b160b;
      font-size: clamp(32px, 4.4vw, 60px);
      font-weight: 900;
      line-height: 1.02;
      text-align: center;
      text-shadow: 0 2px 0 rgba(255, 238, 188, 0.32);
    }

    .world-badge {
      display: grid;
      place-items: center;
      min-width: 138px;
      min-height: 100px;
      padding: 12px;
      border: 3px solid #7b4b22;
      border-radius: 8px;
      background:
        radial-gradient(circle at 50% 38%, rgba(33, 199, 255, 0.36), transparent 54%),
        linear-gradient(180deg, #0d5a84, #17314b);
      color: #ffe8a3;
      text-align: center;
      font-size: 17px;
      font-weight: 900;
      line-height: 1.1;
      box-shadow: 0 0 24px rgba(33, 199, 255, 0.26), inset 0 0 18px rgba(33, 199, 255, 0.14);
    }

    /* Mission surfaces */
    .mission-grid {
      display: grid;
      grid-template-columns: minmax(210px, 0.36fr) minmax(0, 0.64fr);
      gap: 14px;
      align-items: stretch;
    }

    .word-panel,
    .formed-panel,
    .portal-panel {
      display: grid;
      gap: 8px;
      padding: 14px;
      border: 3px solid #6c4728;
      border-radius: 8px;
      background:
        linear-gradient(180deg, rgba(255, 238, 188, 0.14), rgba(54, 31, 22, 0.16)),
        #c99955;
      box-shadow: inset 0 0 24px rgba(43, 22, 11, 0.18), 0 8px 18px rgba(43, 22, 11, 0.24);
    }

    .target,
    .formed {
      min-height: 110px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: clamp(46px, 7vw, 92px);
      font-weight: 900;
      line-height: 1;
      overflow-wrap: anywhere;
      text-align: center;
      text-shadow: 0 4px 0 rgba(0, 0, 0, 0.26);
    }

    .target {
      border: 4px solid #4b2b19;
      background:
        radial-gradient(circle at center, rgba(255, 208, 95, 0.24), rgba(28, 24, 22, 0.82) 68%),
        #211719;
      color: #ffe8a3;
      box-shadow: 0 0 24px rgba(246, 196, 83, 0.36), inset 0 0 20px rgba(0, 0, 0, 0.40);
    }

    .formed {
      min-height: 86px;
      border: 4px solid #4b2b19;
      background: radial-gradient(circle at center, rgba(33, 199, 255, 0.14), rgba(28, 27, 30, 0.88));
      color: #d6fbff;
      font-size: clamp(36px, 5vw, 66px);
    }

    .blocks {
      min-height: 190px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      flex-wrap: wrap;
      padding: 18px;
      border: 4px solid #4b2b19;
      border-radius: 8px;
      background:
        radial-gradient(circle at 50% 55%, rgba(33, 199, 255, 0.32), transparent 56%),
        radial-gradient(circle at 50% 50%, rgba(29, 57, 115, 0.56), transparent 72%),
        #08172b;
      box-shadow: inset 0 0 38px rgba(33, 199, 255, 0.28), 0 0 30px rgba(33, 199, 255, 0.22);
    }

    .block {
      min-width: 98px;
      min-height: 88px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 18px;
      border: 4px solid #8b5b28;
      border-radius: 8px;
      background:
        linear-gradient(180deg, #e1bb73, #a56d2f 58%, #5b341c);
      color: #2b160b;
      font-size: clamp(34px, 5vw, 60px);
      font-weight: 900;
      line-height: 1;
      text-shadow: 0 1px 0 rgba(255, 238, 188, 0.42);
      box-shadow: 0 9px 0 #4b2b19, 0 14px 26px rgba(0, 0, 0, 0.38), inset 0 2px 0 rgba(255, 255, 255, 0.30);
      animation: tileIn 190ms ease-out;
    }

    .block.correct {
      border-color: rgba(153, 255, 170, 0.88);
      background: linear-gradient(180deg, #3f9f54, #226b36);
      color: #f2fff0;
      box-shadow: 0 9px 0 #164823, 0 0 24px rgba(85, 214, 107, 0.34);
    }

    .block.wrong {
      border-color: rgba(255, 224, 130, 0.92);
      background: linear-gradient(180deg, #bf7b2e, #7a431f);
      color: #fff4d6;
      box-shadow: 0 9px 0 #4b2818, 0 0 20px rgba(255, 176, 32, 0.22);
    }

    .empty-blocks {
      color: #ffe8a3;
      font-size: clamp(22px, 3vw, 34px);
      font-weight: 900;
      text-align: center;
      text-shadow: 0 0 18px rgba(246, 196, 83, 0.26);
    }

    @keyframes tileIn {
      from { opacity: 0; transform: translateY(10px) scale(0.95); filter: brightness(1.4); }
      to { opacity: 1; transform: translateY(0) scale(1); filter: brightness(1); }
    }

    /* Feedback and progress */
    .feedback {
      min-height: 86px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px 20px;
      border: 4px solid #4b2b19;
      border-radius: 8px;
      background: linear-gradient(180deg, #0c5f90, #073653);
      color: #e2f9ff;
      font-size: clamp(24px, 3.2vw, 42px);
      font-weight: 900;
      line-height: 1.12;
      text-align: center;
      text-shadow: 0 3px 0 rgba(0, 0, 0, 0.25);
      box-shadow: inset 0 0 22px rgba(33, 199, 255, 0.24), 0 0 18px rgba(33, 199, 255, 0.16);
    }

    .feedback.success {
      border-color: #4b2b19;
      background: linear-gradient(180deg, #2f8f46, #155729);
      color: #f2fff0;
      animation: celebrate 440ms ease-out;
      box-shadow: 0 0 28px rgba(85, 214, 107, 0.28), inset 0 0 18px rgba(242, 255, 240, 0.12);
    }

    .feedback.try_again {
      border-color: #4b2b19;
      background: linear-gradient(180deg, #bf7b2e, #7a431f);
      color: #fff4d6;
    }

    .feedback.demo_complete {
      border-color: #4b2b19;
      background: linear-gradient(180deg, #4f9f5f, #23613d);
      color: #fff8d6;
      box-shadow: 0 0 34px rgba(246, 196, 83, 0.32);
    }

    @keyframes celebrate {
      0% { transform: scale(1); }
      45% { transform: scale(1.025); }
      100% { transform: scale(1); }
    }

    .progress-area {
      display: grid;
      gap: 10px;
    }

    .progress-label {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: #4b2b19;
      font-size: 15px;
      font-weight: 900;
    }

    .progress {
      height: 22px;
      overflow: hidden;
      border: 3px solid #5a331d;
      border-radius: 999px;
      background: rgba(43, 22, 11, 0.92);
      box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.42);
    }

    .progress-bar {
      width: 0%;
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #075b88, #21c7ff, #50d76c, #f6c453);
      box-shadow: 0 0 18px rgba(33, 199, 255, 0.42);
      transition: width 180ms ease;
    }

    .final-message {
      display: none;
      padding: 18px;
      border: 3px solid rgba(255, 232, 163, 0.74);
      border-radius: 8px;
      background: linear-gradient(180deg, #2f8f46, #155729);
      color: #fff8d6;
      font-size: clamp(24px, 3vw, 38px);
      font-weight: 900;
      line-height: 1.12;
      text-align: center;
      box-shadow: 0 0 28px rgba(246, 196, 83, 0.28);
    }

    .final-message.visible {
      display: block;
    }

    /* Controls */
    .side {
      display: grid;
      gap: 14px;
    }

    .side-card {
      display: grid;
      gap: 14px;
      padding: 16px;
      background:
        linear-gradient(180deg, rgba(255, 232, 163, 0.08), transparent 22%),
        linear-gradient(180deg, #4f2c19, #21120a);
    }

    .side-card h2 {
      color: #ffe8a3;
      font-size: 24px;
      line-height: 1.05;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.38);
    }

    .button-grid,
    .command-grid {
      display: grid;
      gap: 10px;
    }

    .button-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .command-grid {
      grid-template-columns: 1fr;
    }

    .manual-button {
      min-height: 62px;
      border: 4px solid #8b5b28;
      border-radius: 8px;
      background: linear-gradient(180deg, #e1bb73, #a56d2f 58%, #5b341c);
      color: #2b160b;
      font-size: 25px;
      font-weight: 900;
      cursor: pointer;
      text-shadow: 0 1px 0 rgba(255, 238, 188, 0.45);
      box-shadow: 0 7px 0 #3f2314, 0 12px 22px rgba(0, 0, 0, 0.34), inset 0 2px 0 rgba(255, 255, 255, 0.28);
    }

    .manual-button:hover {
      filter: brightness(1.12);
    }

    .manual-button.command {
      min-height: 54px;
      border-color: #4b2b19;
      background: linear-gradient(180deg, #075b88, #063653);
      color: #d6fbff;
      font-size: 18px;
      box-shadow: 0 6px 0 #100b17, 0 0 18px rgba(45, 212, 255, 0.18);
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
      .layout,
      .mission-head,
      .mission-grid {
        grid-template-columns: 1fr;
      }

      .world-badge {
        min-height: 74px;
      }
    }
  </style>
</head>
<body>
  <main>
    <header class="topbar">
      <div class="brand">
        <h1>SilaBlocks</h1>
        <p class="subtitle">El Mundo de las Palabras Perdidas</p>
      </div>
      <div class="connection" id="connection">Conectando</div>
    </header>

    <div class="layout">
      <section class="mission-card" aria-label="Misión actual">
        <div class="mission-head">
          <div>
            <div class="mission-pill" id="missionCounter">Misión 1 de 5</div>
            <p class="prompt" id="prompt">Reconstruye la palabra</p>
          </div>
          <div class="world-badge" id="worldBadge">Mundo por restaurar</div>
        </div>

        <div class="final-message" id="finalMessage">Completaste todas las misiones.</div>

        <div class="mission-grid">
          <div class="word-panel">
            <div class="label">Palabra perdida</div>
            <div class="target" id="target">MAMÁ</div>
          </div>
          <div class="formed-panel">
            <div class="label">Palabra formada</div>
            <div class="formed" id="formed">-</div>
          </div>
        </div>

        <div class="portal-panel">
          <div class="label">Portal de bloques</div>
          <div class="blocks" id="blocks"></div>
        </div>

        <div class="feedback" id="feedback">Escanea un cubo para comenzar.</div>

        <div class="progress-area">
          <div class="progress-label">
            <span>Palabra actual</span>
            <span id="missionProgressText">0%</span>
          </div>
          <div class="progress" aria-hidden="true">
            <div class="progress-bar" id="progressBar"></div>
          </div>
          <div class="progress-label">
            <span>Restauración del mundo</span>
            <span id="overallProgressText">0 de 5</span>
          </div>
          <div class="progress" aria-hidden="true">
            <div class="progress-bar" id="overallProgressBar"></div>
          </div>
        </div>
      </section>

      <aside class="side" aria-label="Controles y estado">
        <section class="side-card">
          <h2>Cubos sugeridos</h2>
          <div class="button-grid" id="inputButtons"></div>
        </section>

        <section class="side-card">
          <h2>Acciones</h2>
          <div class="command-grid" id="commandButtons"></div>
        </section>
      </aside>
    </div>
  </main>

  <script>
    const commands = ["BORRAR", "RESET", "SIGUIENTE", "ANTERIOR"];

    const ids = {
      connection: document.getElementById("connection"),
      prompt: document.getElementById("prompt"),
      missionCounter: document.getElementById("missionCounter"),
      worldBadge: document.getElementById("worldBadge"),
      finalMessage: document.getElementById("finalMessage"),
      target: document.getElementById("target"),
      formed: document.getElementById("formed"),
      blocks: document.getElementById("blocks"),
      feedback: document.getElementById("feedback"),
      progressBar: document.getElementById("progressBar"),
      missionProgressText: document.getElementById("missionProgressText"),
      overallProgressText: document.getElementById("overallProgressText"),
      overallProgressBar: document.getElementById("overallProgressBar"),
      inputButtons: document.getElementById("inputButtons"),
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

    function renderInputButtons(availableBlocks) {
      ids.inputButtons.innerHTML = "";
      availableBlocks.forEach((value) => {
        ids.inputButtons.appendChild(createButton(value, "manual-button"));
      });
    }

    async function sendNfc(value) {
      const response = await fetch(`/nfc?letra=${encodeURIComponent(value)}`);
      const payload = await response.json();
      render(payload);
    }

    function visiblePrompt(prompt, targetText) {
      const fallback = "Reconstruye la palabra";
      if (!prompt) {
        return fallback;
      }
      if (!targetText) {
        return prompt;
      }
      const cleaned = prompt.replace(targetText, "").replace(/\\s+/g, " ").trim();
      return cleaned || fallback;
    }

    function render(payload) {
      const blocks = payload.current_blocks || payload.bloques || [];
      const targetBlocks = payload.target_blocks || [];
      const availableBlocks = payload.available_blocks || [];
      const targetLength = Math.max(targetBlocks.length, 1);
      const fallbackProgress = Math.min(100, Math.round((blocks.length / targetLength) * 100));
      const progress = Number.isFinite(payload.progress_percent) ? payload.progress_percent : fallbackProgress;
      const missionNumber = payload.mission_number || 1;
      const totalMissions = payload.total_missions || 1;
      const completedMissions = payload.completed_missions || 0;
      const overallProgress = Number.isFinite(payload.overall_progress_percent)
        ? payload.overall_progress_percent
        : Math.round((completedMissions / totalMissions) * 100);

      ids.prompt.textContent = visiblePrompt(payload.prompt, payload.target_text);
      ids.missionCounter.textContent = `Misión ${missionNumber} de ${totalMissions}`;
      ids.worldBadge.textContent = payload.is_demo_complete ? "Mundo restaurado" : `${completedMissions} de ${totalMissions} partes`;
      ids.target.textContent = payload.target_text || "MAMÁ";
      ids.formed.textContent = payload.current_text || "-";
      ids.feedback.textContent = payload.feedback || "";
      ids.feedback.className = `feedback ${payload.status || "idle"}`;
      ids.progressBar.style.width = `${payload.status === "success" ? 100 : progress}%`;
      ids.missionProgressText.textContent = `${payload.status === "success" ? 100 : progress}%`;
      ids.overallProgressText.textContent = `${completedMissions} de ${totalMissions}`;
      ids.overallProgressBar.style.width = `${overallProgress}%`;
      ids.finalMessage.className = `final-message ${payload.is_demo_complete ? "visible" : ""}`;
      ids.blocks.innerHTML = "";
      if (blocks.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-blocks";
        empty.textContent = "Escanea un cubo para abrir el portal";
        ids.blocks.appendChild(empty);
      } else {
        blocks.forEach((block, index) => {
          const item = document.createElement("div");
          const isCorrect = targetBlocks[index] === block;
          const isKnownPosition = index < targetBlocks.length;
          item.className = `block ${isCorrect ? "correct" : isKnownPosition ? "wrong" : ""}`;
          item.textContent = block;
          ids.blocks.appendChild(item);
        });
      }

      renderInputButtons(availableBlocks);
    }

    async function loadInitialState() {
      const response = await fetch("/buffer");
      const payload = await response.json();
      render(payload);
    }

    function connectSocket() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

      socket.addEventListener("open", () => {
        ids.connection.textContent = "Conectado";
      });

      socket.addEventListener("message", (event) => {
        render(JSON.parse(event.data));
      });

      socket.addEventListener("close", () => {
        ids.connection.textContent = "Reconectando";
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


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
