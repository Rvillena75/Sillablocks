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
ENTER_COMMAND = "ENTER"
KNOWN_COMMANDS = DELETE_COMMANDS | {RESET_COMMAND, ENTER_COMMAND}

INITIAL_MISSION = {
    "mission_id": "m001",
    "prompt": "Reconstruye la palabra MAMÁ",
    "target_blocks": ["MA", "MÁ"],
    "accepted_answers": ["MAMÁ"],
    "available_blocks": ["MA", "MÁ", "PA", "SA"],
}

FEEDBACK_EMPTY = "Escanea un cubo para comenzar."
FEEDBACK_IN_PROGRESS = "Vas bien. Falta una parte."
FEEDBACK_SUCCESS = "Muy bien. Reconstruiste la palabra MAMÁ."
FEEDBACK_TRY_AGAIN = "Casi. Prueba otra combinación."
FEEDBACK_KEEP_TRYING = "Sigue probando con los cubos."
FEEDBACK_WRONG_BLOCK = "Casi. Revisa el último cubo y prueba otra combinación."


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("sillablocks")

app = FastAPI(title="SilaBlocks NFC Server")

current_blocks: list[str] = []
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


def is_prefix_of_target(blocks: list[str]) -> bool:
    target_blocks = INITIAL_MISSION["target_blocks"]
    if len(blocks) > len(target_blocks):
        return False
    return blocks == target_blocks[: len(blocks)]


def is_exact_target_blocks(blocks: list[str]) -> bool:
    return blocks == INITIAL_MISSION["target_blocks"]


def correct_prefix_count(blocks: list[str]) -> int:
    target_blocks = INITIAL_MISSION["target_blocks"]
    count = 0
    for index, block in enumerate(blocks):
        if index >= len(target_blocks) or block != target_blocks[index]:
            break
        count += 1
    return count


def progress_percent() -> int:
    target_count = max(len(INITIAL_MISSION["target_blocks"]), 1)
    return round((correct_prefix_count(current_blocks) / target_count) * 100)


def expected_next_block() -> str | None:
    count = correct_prefix_count(current_blocks)
    target_blocks = INITIAL_MISSION["target_blocks"]
    if count < len(target_blocks):
        return target_blocks[count]
    return None


def is_available_block(value: str) -> bool:
    return value in INITIAL_MISSION["available_blocks"]


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


def evaluate_game_state(validate_now: bool = False) -> None:
    global game_status, feedback

    if not current_blocks:
        game_status = "idle"
        feedback = FEEDBACK_EMPTY
        return

    if is_exact_target_blocks(current_blocks):
        game_status = "success"
        feedback = FEEDBACK_SUCCESS
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
    current_blocks.clear()
    last_ignored_input = None
    last_action = "reset"
    evaluate_game_state()


def build_state(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    text = current_text()
    correct_count = correct_prefix_count(current_blocks)
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
        "mission_id": INITIAL_MISSION["mission_id"],
        "prompt": INITIAL_MISSION["prompt"],
        "target_text": INITIAL_MISSION["accepted_answers"][0],
        "target_blocks": list(INITIAL_MISSION["target_blocks"]),
        "accepted_answers": list(INITIAL_MISSION["accepted_answers"]),
        "available_blocks": list(INITIAL_MISSION["available_blocks"]),
        "correct_prefix_count": correct_count,
        "target_block_count": len(INITIAL_MISSION["target_blocks"]),
        "progress_percent": 100 if game_status == "success" else progress_percent(),
        "expected_next_block": expected_next_block(),
        "has_block_mismatch": bool(current_blocks) and not is_prefix_of_target(current_blocks),
        "status": game_status,
        "feedback": feedback,
        "mission": dict(INITIAL_MISSION),
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
    elif value == ENTER_COMMAND:
        last_action = "validate"
        last_input = value
        evaluate_game_state(validate_now=True)
    elif game_status == "success":
        last_action = "ignored_after_success"
        last_ignored_input = value
        accepted = False
    elif not is_available_block(value):
        last_action = "ignored"
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
        "mission_id": INITIAL_MISSION["mission_id"],
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
  <title>SilaBlocks MVP</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #1f2937;
      --muted: #526071;
      --line: #d7dde6;
      --paper: #f8fafc;
      --panel: #ffffff;
      --accent: #087f5b;
      --accent-soft: #d3f9d8;
      --focus: #0b7285;
      --warn: #f08c00;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--paper);
    }

    main {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 36px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }

    h1,
    h2,
    p {
      margin: 0;
    }

    h1 {
      font-size: clamp(28px, 5vw, 54px);
      line-height: 1.05;
    }

    .connection {
      min-width: 145px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--muted);
      font-weight: 700;
      text-align: center;
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
      gap: 18px;
    }

    .section {
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }

    .mission {
      display: grid;
      gap: 18px;
      min-height: 620px;
    }

    .prompt {
      font-size: clamp(26px, 4.5vw, 58px);
      line-height: 1.08;
      font-weight: 800;
    }

    .target-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .label {
      color: var(--muted);
      font-size: 15px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .target,
    .formed {
      min-height: 96px;
      display: flex;
      align-items: center;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      font-size: clamp(42px, 7vw, 86px);
      font-weight: 900;
      line-height: 1;
      overflow-wrap: anywhere;
      background: #fff;
    }

    .target {
      color: var(--focus);
    }

    .blocks {
      min-height: 114px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      padding: 14px;
      border: 2px dashed #adb5bd;
      border-radius: 8px;
      background: #f1f5f9;
    }

    .block {
      min-width: 88px;
      min-height: 78px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 16px;
      border: 2px solid #364fc7;
      border-radius: 8px;
      background: #edf2ff;
      color: #1c2f8f;
      font-size: clamp(28px, 5vw, 52px);
      font-weight: 900;
      line-height: 1;
    }

    .block.correct {
      border-color: #087f5b;
      background: #d3f9d8;
      color: #116329;
    }

    .block.wrong {
      border-color: #e67700;
      background: #fff3bf;
      color: #7c4d00;
    }

    .empty-blocks {
      color: var(--muted);
      font-size: clamp(21px, 3vw, 30px);
      font-weight: 700;
    }

    .feedback {
      min-height: 94px;
      display: flex;
      align-items: center;
      padding: 18px 20px;
      border-radius: 8px;
      background: #e7f5ff;
      color: #0b4f6c;
      font-size: clamp(26px, 4vw, 46px);
      font-weight: 800;
      line-height: 1.12;
    }

    .feedback.success {
      background: var(--accent-soft);
      color: #116329;
    }

    .feedback.try_again {
      background: #fff3bf;
      color: #7c4d00;
    }

    .progress {
      height: 18px;
      overflow: hidden;
      border-radius: 999px;
      background: #e9ecef;
    }

    .progress-bar {
      width: 0%;
      height: 100%;
      background: var(--accent);
      transition: width 160ms ease;
    }

    .controls,
    .debug {
      display: grid;
      gap: 12px;
    }

    .button-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    button {
      min-height: 56px;
      border: 1px solid #97a3b3;
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      font-size: 20px;
      font-weight: 800;
      cursor: pointer;
    }

    button:hover {
      border-color: var(--focus);
      background: #e7f5ff;
    }

    button.command {
      color: #5c3c00;
      background: #fff9db;
    }

    button.primary {
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
    }

    .debug-list {
      display: grid;
      gap: 8px;
      font-size: 15px;
    }

    .debug-row {
      display: grid;
      grid-template-columns: 130px minmax(0, 1fr);
      gap: 8px;
      padding: 8px 0;
      border-bottom: 1px solid #edf2f7;
    }

    .debug-key {
      color: var(--muted);
      font-weight: 700;
    }

    .debug-value {
      overflow-wrap: anywhere;
      font-family: Consolas, "Courier New", monospace;
      color: #111827;
    }

    .event-list {
      display: grid;
      gap: 6px;
      margin-top: 4px;
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
      color: #111827;
    }

    .event-item {
      padding: 6px 8px;
      border-radius: 6px;
      background: #f1f5f9;
      overflow-wrap: anywhere;
    }

    @media (max-width: 820px) {
      main {
        width: min(100vw - 20px, 680px);
        padding-top: 16px;
      }

      .topbar,
      .layout,
      .target-row {
        grid-template-columns: 1fr;
        display: grid;
      }

      .mission {
        min-height: auto;
      }
    }
  </style>
</head>
<body>
  <main>
    <div class="topbar">
      <h1>SilaBlocks</h1>
      <div class="connection" id="connection">Conectando</div>
    </div>

    <div class="layout">
      <section class="section mission" aria-label="Misión actual">
        <div>
          <div class="label">Misión</div>
          <p class="prompt" id="prompt">Reconstruye la palabra MAMÁ</p>
        </div>

        <div class="target-row">
          <div>
            <div class="label">Objetivo</div>
            <div class="target" id="target">MAMÁ</div>
          </div>
          <div>
            <div class="label">Palabra formada</div>
            <div class="formed" id="formed">-</div>
          </div>
        </div>

        <div>
          <div class="label">Cubos escaneados</div>
          <div class="blocks" id="blocks"></div>
        </div>

        <div class="feedback" id="feedback">Escanea un cubo para comenzar.</div>

        <div>
          <div class="label">Progreso</div>
          <div class="progress" aria-hidden="true">
            <div class="progress-bar" id="progressBar"></div>
          </div>
        </div>
      </section>

      <aside class="controls">
        <section class="section">
          <h2>Prueba manual</h2>
          <div class="button-grid" id="manualButtons"></div>
        </section>

        <section class="section debug">
          <h2>Debug</h2>
          <div class="debug-list">
            <div class="debug-row"><div class="debug-key">Último recibido</div><div class="debug-value" id="debugReceived">-</div></div>
            <div class="debug-row"><div class="debug-key">Último aceptado</div><div class="debug-value" id="debugLast">-</div></div>
            <div class="debug-row"><div class="debug-key">Último ignorado</div><div class="debug-value" id="debugIgnored">-</div></div>
            <div class="debug-row"><div class="debug-key">Acción</div><div class="debug-value" id="debugAction">init</div></div>
            <div class="debug-row"><div class="debug-key">Bloques</div><div class="debug-value" id="debugBlocks">[]</div></div>
            <div class="debug-row"><div class="debug-key">Texto</div><div class="debug-value" id="debugText">-</div></div>
            <div class="debug-row"><div class="debug-key">Misión</div><div class="debug-value" id="debugMission">m001</div></div>
            <div class="debug-row"><div class="debug-key">Objetivo</div><div class="debug-value" id="debugTarget">MAMÁ</div></div>
            <div class="debug-row"><div class="debug-key">Estado</div><div class="debug-value" id="debugStatus">idle</div></div>
            <div class="debug-row"><div class="debug-key">Progreso</div><div class="debug-value" id="debugProgress">0%</div></div>
            <div class="debug-row"><div class="debug-key">Siguiente</div><div class="debug-value" id="debugExpected">MA</div></div>
            <div class="debug-row"><div class="debug-key">WebSocket</div><div class="debug-value" id="debugWs">conectando</div></div>
            <div>
              <div class="debug-key">Eventos recientes</div>
              <div class="event-list" id="debugEvents"></div>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </main>

  <script>
    const state = {
      availableBlocks: ["MA", "MÁ", "PA", "SA"],
      commands: ["BORRAR", "RESET", "ENTER"]
    };

    const ids = {
      connection: document.getElementById("connection"),
      prompt: document.getElementById("prompt"),
      target: document.getElementById("target"),
      formed: document.getElementById("formed"),
      blocks: document.getElementById("blocks"),
      feedback: document.getElementById("feedback"),
      progressBar: document.getElementById("progressBar"),
      manualButtons: document.getElementById("manualButtons"),
      debugReceived: document.getElementById("debugReceived"),
      debugLast: document.getElementById("debugLast"),
      debugIgnored: document.getElementById("debugIgnored"),
      debugAction: document.getElementById("debugAction"),
      debugBlocks: document.getElementById("debugBlocks"),
      debugText: document.getElementById("debugText"),
      debugMission: document.getElementById("debugMission"),
      debugTarget: document.getElementById("debugTarget"),
      debugStatus: document.getElementById("debugStatus"),
      debugProgress: document.getElementById("debugProgress"),
      debugExpected: document.getElementById("debugExpected"),
      debugWs: document.getElementById("debugWs"),
      debugEvents: document.getElementById("debugEvents")
    };

    function renderButtons() {
      [...state.availableBlocks, ...state.commands].forEach((value) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = value;
        if (state.commands.includes(value)) {
          button.className = value === "ENTER" ? "primary" : "command";
        }
        button.addEventListener("click", () => sendNfc(value));
        ids.manualButtons.appendChild(button);
      });
    }

    async function sendNfc(value) {
      const response = await fetch(`/nfc?letra=${encodeURIComponent(value)}`);
      const payload = await response.json();
      render(payload);
    }

    function render(payload) {
      const blocks = payload.current_blocks || payload.bloques || [];
      const targetBlocks = payload.target_blocks || [];
      const targetLength = Math.max(targetBlocks.length, 1);
      const fallbackProgress = Math.min(100, Math.round((blocks.length / targetLength) * 100));
      const progress = Number.isFinite(payload.progress_percent) ? payload.progress_percent : fallbackProgress;

      ids.prompt.textContent = payload.prompt || "Reconstruye la palabra MAMÁ";
      ids.target.textContent = payload.target_text || "MAMÁ";
      ids.formed.textContent = payload.current_text || "-";
      ids.feedback.textContent = payload.feedback || "";
      ids.feedback.className = `feedback ${payload.status || "idle"}`;
      ids.progressBar.style.width = `${payload.status === "success" ? 100 : progress}%`;

      ids.blocks.innerHTML = "";
      if (blocks.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-blocks";
        empty.textContent = "Esperando cubos NFC";
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

      ids.debugReceived.textContent = payload.last_received_input || payload.ultimo_recibido || "-";
      ids.debugLast.textContent = payload.last_input || payload.ultimo_input || "-";
      ids.debugIgnored.textContent = payload.last_ignored_input || payload.ultimo_ignorado || "-";
      ids.debugAction.textContent = payload.action || payload.accion || "-";
      ids.debugBlocks.textContent = JSON.stringify(blocks);
      ids.debugText.textContent = payload.current_text || "-";
      ids.debugMission.textContent = payload.mission_id || "-";
      ids.debugTarget.textContent = payload.target_text || "-";
      ids.debugStatus.textContent = payload.status || "-";
      ids.debugProgress.textContent = `${progress}%`;
      ids.debugExpected.textContent = payload.expected_next_block || "-";

      ids.debugEvents.innerHTML = "";
      const events = payload.recent_inputs || [];
      if (events.length === 0) {
        const empty = document.createElement("div");
        empty.className = "event-item";
        empty.textContent = "Sin eventos";
        ids.debugEvents.appendChild(empty);
      } else {
        events.slice().reverse().forEach((event) => {
          const item = document.createElement("div");
          item.className = "event-item";
          item.textContent = `${event.value} | ${event.action} | ${event.accepted ? "aceptado" : "ignorado"}`;
          ids.debugEvents.appendChild(item);
        });
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

      socket.addEventListener("open", () => {
        ids.connection.textContent = "Conectado";
        ids.debugWs.textContent = "conectado";
      });

      socket.addEventListener("message", (event) => {
        render(JSON.parse(event.data));
      });

      socket.addEventListener("close", () => {
        ids.connection.textContent = "Reconectando";
        ids.debugWs.textContent = "reconectando";
        window.setTimeout(connectSocket, 1200);
      });
    }

    renderButtons();
    loadInitialState();
    connectSocket();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
