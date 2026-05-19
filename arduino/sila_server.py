from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from arduino.game.engine import (  # noqa: E402
    DELETE_COMMANDS,
    ENTER_COMMAND,
    KNOWN_COMMANDS,
    NEXT_COMMAND,
    PREVIOUS_COMMAND,
    RESET_ALL_COMMAND,
    RESET_COMMAND,
    GameEngine,
)
from arduino.game.missions import (  # noqa: E402
    FEEDBACK_DEMO_COMPLETE,
    FEEDBACK_EMPTY,
    FEEDBACK_FIRST_MISSION,
    FEEDBACK_IN_PROGRESS,
    FEEDBACK_KEEP_TRYING,
    FEEDBACK_NEXT_BLOCKED,
    FEEDBACK_SUCCESS,
    FEEDBACK_SUCCESS_TEMPLATE,
    FEEDBACK_TRY_AGAIN,
    FEEDBACK_WRONG_BLOCK,
    MISSIONS as GAME_MISSIONS,
)
from arduino.game.progress import GameProgress, ProgressStore  # noqa: E402
from arduino.game.shop import (  # noqa: E402
    SHOP_ITEM_BY_ID,
    build_shop_payload,
    buy_shop_item,
)


HOST = "0.0.0.0"
PORT = 5000
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"
INDEX_TEMPLATE = TEMPLATE_DIR / "index.html"
ALDEA_TEMPLATE = TEMPLATE_DIR / "aldea.html"

MISSIONS = [mission.as_dict() for mission in GAME_MISSIONS]
FRAGMENT_REWARD_COMPLETION_COUNTS = {3, 5}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("sillablocks")

app = FastAPI(title="SilaBlocks NFC Server")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

game_engine = GameEngine()
progress_store = ProgressStore()

# Backwards-compatible module-level state for tests and quick debugging.
current_blocks = game_engine.current_blocks
completed_mission_ids = game_engine.completed_mission_ids
recent_inputs = game_engine.recent_inputs
current_mission_index = game_engine.current_mission_index
last_input: str | None = game_engine.last_input
last_received_input: str | None = game_engine.last_received_input
last_ignored_input: str | None = game_engine.last_ignored_input
last_action = game_engine.last_action
game_status = game_engine.status
feedback = game_engine.feedback


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


class BuyRequest(BaseModel):
    item_id: str


class DecorationPlaceRequest(BaseModel):
    item_id: str
    x: float
    y: float


class DecorationMoveRequest(BaseModel):
    x: float
    y: float


class MissionSelectRequest(BaseModel):
    mission_id: str


def sync_legacy_state() -> None:
    global current_mission_index, last_input, last_received_input
    global last_ignored_input, last_action, game_status, feedback

    current_mission_index = game_engine.current_mission_index
    last_input = game_engine.last_input
    last_received_input = game_engine.last_received_input
    last_ignored_input = game_engine.last_ignored_input
    last_action = game_engine.last_action
    game_status = game_engine.status
    feedback = game_engine.feedback


def apply_progress_to_engine(progress: GameProgress) -> None:
    game_engine.lumens = progress.lumens
    game_engine.map_fragments = progress.fragments

    game_engine.completed_mission_ids.clear()
    game_engine.completed_mission_ids.update(progress.completed_missions)

    game_engine.rewarded_mission_ids.clear()
    game_engine.rewarded_mission_ids.update(progress.completed_missions)

    game_engine.restored_items.clear()
    game_engine.restored_items.extend(progress.restored_items)
    sync_legacy_state()


def load_persisted_progress() -> GameProgress:
    progress = progress_store.load()
    apply_progress_to_engine(progress)
    return progress


def reset_demo_state_on_startup() -> GameProgress:
    game_engine.reset_runtime()
    progress = progress_store.reset()
    apply_progress_to_engine(progress)
    logger.info("Demo state reset on startup")
    return progress


def build_progress_payload(progress: GameProgress | None = None) -> dict[str, Any]:
    current_progress = progress if progress is not None else progress_store.load()
    payload = current_progress.to_dict()
    payload["ok"] = True
    payload["map_fragments"] = current_progress.fragments
    return payload


def build_buy_payload(
    result_code: str,
    message: str,
    progress: GameProgress,
    ok: bool,
    item: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "code": result_code,
        "message": message,
        "item": item,
        "progress": build_progress_payload(progress),
        "events": [] if events is None else events,
    }


def normalize_decoration_position(x: float, y: float) -> dict[str, int] | None:
    if not 0 <= x <= 100 or not 0 <= y <= 100:
        return None
    return {"x": round(x), "y": round(y)}


def next_decoration_id(progress: GameProgress) -> str:
    highest = 0
    for decoration in progress.placed_decorations:
        decoration_id = str(decoration.get("id", ""))
        if not decoration_id.startswith("decor_"):
            continue
        try:
            highest = max(highest, int(decoration_id.removeprefix("decor_")))
        except ValueError:
            continue
    return f"decor_{highest + 1:03d}"


def build_decoration_payload(
    progress: GameProgress,
    decoration: dict[str, Any] | None,
    message: str,
    ok: bool = True,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "message": message,
        "decoration": decoration,
        "progress": build_progress_payload(progress),
        "events": events or [],
    }


def owned_decoration_count(progress: GameProgress, item_id: str) -> int:
    return progress.purchased_items.count(item_id)


def placed_decoration_count(progress: GameProgress, item_id: str) -> int:
    return sum(
        1
        for decoration in progress.placed_decorations
        if decoration.get("item_id") == item_id
    )


def previous_missions_completed(mission_index: int, progress: GameProgress) -> bool:
    completed = set(progress.completed_missions)
    completed.update(game_engine.completed_mission_ids)
    return all(
        mission.mission_id in completed
        for mission in game_engine.missions[:mission_index]
    )


def build_mission_completion_events(
    mission: Any,
    reward_lumens: int,
    reward_fragments: int,
) -> list[dict[str, Any]]:
    return [
        {
            "type": "mission_completed",
            "mission_id": mission.mission_id,
            "target_text": mission.accepted_answers[0],
        },
        {
            "type": "reward_granted",
            "mission_id": mission.mission_id,
            "lumens": reward_lumens,
            "fragments": reward_fragments,
        },
        {
            "type": "scene_restored",
            "mission_id": mission.mission_id,
            "item": mission.restoration,
        },
    ]


def persist_completed_missions() -> tuple[GameProgress, list[dict[str, Any]]]:
    progress = progress_store.load()
    changed = False
    events: list[dict[str, Any]] = []

    for mission in game_engine.missions:
        if mission.mission_id not in game_engine.completed_mission_ids:
            continue
        if mission.mission_id in progress.completed_missions:
            continue

        reward_fragments = 0
        progress.mark_mission_completed(mission.mission_id)
        progress.add_rewards(lumens=mission.reward_lumens)
        if len(progress.completed_missions) in FRAGMENT_REWARD_COMPLETION_COUNTS:
            reward_fragments = 1
            progress.add_rewards(fragments=reward_fragments)
        progress.mark_item_restored(mission.restoration)
        events.extend(
            build_mission_completion_events(
                mission,
                reward_lumens=mission.reward_lumens,
                reward_fragments=reward_fragments,
            )
        )
        changed = True

    if changed:
        progress = progress_store.save(progress)
        apply_progress_to_engine(progress)

    return progress, events


def reset_runtime_state() -> None:
    game_engine.reset_runtime()
    progress = progress_store.reset()
    apply_progress_to_engine(progress)
    sync_legacy_state()


def normalize_input(value: str | None) -> str:
    return game_engine.normalize_input(value)


def current_text() -> str:
    return game_engine.current_text()


def current_mission() -> dict[str, Any]:
    return game_engine.current_mission().as_dict()


def target_text() -> str:
    return game_engine.target_text()


def mission_number() -> int:
    return game_engine.mission_number()


def total_missions() -> int:
    return game_engine.total_missions()


def is_last_mission() -> bool:
    return game_engine.is_last_mission()


def is_prefix_of_target(blocks: list[str]) -> bool:
    return game_engine.is_prefix_of_target(blocks)


def is_exact_target_blocks(blocks: list[str]) -> bool:
    return game_engine.is_exact_target_blocks(blocks)


def correct_prefix_count(blocks: list[str]) -> int:
    return game_engine.correct_prefix_count(blocks)


def progress_percent() -> int:
    return game_engine.progress_percent()


def expected_next_block() -> str | None:
    return game_engine.expected_next_block()


def remember_input(value: str, action: str, accepted: bool) -> None:
    game_engine.remember_input(value, action, accepted)
    sync_legacy_state()


def mark_current_mission_completed() -> None:
    game_engine.complete_current_mission()
    sync_legacy_state()


def clear_current_buffer() -> None:
    game_engine.buffer.clear()
    sync_legacy_state()


def evaluate_game_state(validate_now: bool = False) -> None:
    game_engine.evaluate_game_state(validate_now)
    sync_legacy_state()


def reset_game_state() -> None:
    game_engine.reset_current_mission()
    sync_legacy_state()


def reset_all_game_state() -> None:
    game_engine.reset_all()
    progress = progress_store.reset()
    apply_progress_to_engine(progress)
    sync_legacy_state()


def go_to_next_mission() -> bool:
    accepted = game_engine.go_to_next_mission()
    sync_legacy_state()
    return accepted


def go_to_previous_mission() -> bool:
    accepted = game_engine.go_to_previous_mission()
    sync_legacy_state()
    return accepted


def build_state(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    state = game_engine.build_state(
        {
            "websocket_connections": len(manager.active_connections),
            "debug_mode": True,
        }
    )
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

    processed = game_engine.process_input(value)
    events: list[dict[str, Any]] = []
    if processed.action == "reset_all":
        progress = progress_store.reset()
        apply_progress_to_engine(progress)
    else:
        _, events = persist_completed_missions()
    sync_legacy_state()

    logger.info(
        "NFC input=%s action=%s accepted=%s blocks=%s text=%s status=%s lumens=%s",
        processed.value,
        processed.action,
        processed.accepted,
        current_blocks,
        current_text(),
        game_status,
        game_engine.lumens,
    )
    state = build_state(
        {
            "letra": processed.value,
            "valor": processed.value,
            "command": processed.value if processed.value in KNOWN_COMMANDS else None,
            "accepted": processed.accepted,
            "ignored": processed.ignored,
            "events": events,
        }
    )
    await manager.broadcast(build_state({"events": events}))
    return JSONResponse(content=state)


def read_template(path: Path) -> HTMLResponse:
    return HTMLResponse(path.read_text(encoding="utf-8"))


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return read_template(INDEX_TEMPLATE)


@app.get("/aldea", response_class=HTMLResponse)
async def aldea_view() -> HTMLResponse:
    return read_template(ALDEA_TEMPLATE)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "ok",
        "service": "sillablocks",
        "mission_id": game_engine.current_mission().mission_id,
    }


@app.get("/buffer")
async def get_buffer() -> dict[str, Any]:
    return build_state()


@app.get("/progress")
async def get_progress() -> dict[str, Any]:
    return build_progress_payload()


@app.get("/shop")
async def get_shop() -> dict[str, Any]:
    return build_shop_payload(progress_store.load())


@app.post("/buy")
async def buy_item(request: BuyRequest) -> JSONResponse:
    progress = progress_store.load()
    result = buy_shop_item(progress, request.item_id)
    item_payload = result.item.as_dict(progress) if result.item is not None else None

    if not result.ok:
        return JSONResponse(
            status_code=result.status_code,
            content=build_buy_payload(
                result.code,
                result.message,
                progress,
                ok=False,
                item=item_payload,
                events=result.events,
            ),
        )

    saved_progress = progress_store.save(progress)
    apply_progress_to_engine(saved_progress)
    await manager.broadcast(build_state({"events": result.events}))
    return JSONResponse(
        content=build_buy_payload(
            result.code,
            result.message,
            saved_progress,
            ok=True,
            item=result.item.as_dict(saved_progress) if result.item is not None else None,
            events=result.events,
        )
    )


@app.post("/decorations/place")
async def place_decoration(request: DecorationPlaceRequest) -> JSONResponse:
    progress = progress_store.load()
    item_id = request.item_id.strip()
    item = SHOP_ITEM_BY_ID.get(item_id)
    position = normalize_decoration_position(request.x, request.y)

    if item is None:
        return JSONResponse(
            status_code=404,
            content=build_decoration_payload(
                progress,
                None,
                "No encontramos esa decoracion.",
                ok=False,
            ),
        )

    if owned_decoration_count(progress, item_id) <= placed_decoration_count(progress, item_id):
        return JSONResponse(
            status_code=409,
            content=build_decoration_payload(
                progress,
                None,
                "Primero compra otra copia de esa decoracion.",
                ok=False,
            ),
        )

    if position is None:
        return JSONResponse(
            status_code=400,
            content=build_decoration_payload(
                progress,
                None,
                "Elige un lugar dentro de la aldea.",
                ok=False,
            ),
        )

    decoration = {
        "id": next_decoration_id(progress),
        "item_id": item_id,
        "position": position,
        "rotation": 0,
        "scale": 1,
    }
    progress.placed_decorations.append(decoration)
    saved_progress = progress_store.save(progress)
    events = [{"type": "decoration_placed", "decoration": decoration}]
    await manager.broadcast(build_state({"events": events}))
    return JSONResponse(
        content=build_decoration_payload(
            saved_progress,
            decoration,
            "Decoracion colocada en la aldea.",
            events=events,
        )
    )


@app.patch("/decorations/{decoration_id}")
async def move_decoration(decoration_id: str, request: DecorationMoveRequest) -> JSONResponse:
    progress = progress_store.load()
    position = normalize_decoration_position(request.x, request.y)
    decoration = next(
        (
            item
            for item in progress.placed_decorations
            if item.get("id") == decoration_id
        ),
        None,
    )

    if decoration is None:
        return JSONResponse(
            status_code=404,
            content=build_decoration_payload(
                progress,
                None,
                "No encontramos esa decoracion colocada.",
                ok=False,
            ),
        )

    if position is None:
        return JSONResponse(
            status_code=400,
            content=build_decoration_payload(
                progress,
                decoration,
                "Elige un lugar dentro de la aldea.",
                ok=False,
            ),
        )

    decoration["position"] = position
    saved_progress = progress_store.save(progress)
    events = [{"type": "decoration_moved", "decoration": decoration}]
    await manager.broadcast(build_state({"events": events}))
    return JSONResponse(
        content=build_decoration_payload(
            saved_progress,
            decoration,
            "Decoracion reubicada.",
            events=events,
        )
    )


@app.delete("/decorations/{decoration_id}")
async def remove_decoration(decoration_id: str) -> JSONResponse:
    progress = progress_store.load()
    decoration = next(
        (
            item
            for item in progress.placed_decorations
            if item.get("id") == decoration_id
        ),
        None,
    )

    if decoration is None:
        return JSONResponse(
            status_code=404,
            content=build_decoration_payload(
                progress,
                None,
                "No encontramos esa decoracion colocada.",
                ok=False,
            ),
        )

    progress.placed_decorations = [
        item
        for item in progress.placed_decorations
        if item.get("id") != decoration_id
    ]
    saved_progress = progress_store.save(progress)
    events = [{"type": "decoration_removed", "decoration": decoration}]
    await manager.broadcast(build_state({"events": events}))
    return JSONResponse(
        content=build_decoration_payload(
            saved_progress,
            decoration,
            "Decoracion guardada en inventario.",
            events=events,
        )
    )


@app.post("/mission/select")
async def select_mission(request: MissionSelectRequest) -> JSONResponse:
    mission_id = request.mission_id.strip().lower()
    mission_index = game_engine.mission_index_for_id(mission_id)
    if mission_index is None:
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "code": "unknown_mission",
                "message": "Esa misión no existe.",
                "mission_id": mission_id,
            },
        )

    progress = progress_store.load()
    if not previous_missions_completed(mission_index, progress):
        return JSONResponse(
            status_code=409,
            content={
                "ok": False,
                "code": "mission_locked",
                "message": "Primero restaura el objeto anterior.",
                "mission_id": mission_id,
            },
        )

    game_engine.select_mission(mission_id)
    sync_legacy_state()
    state = build_state({"selected": True})
    await manager.broadcast(state)
    return JSONResponse(content=state)


@app.delete("/buffer")
async def delete_buffer() -> dict[str, Any]:
    game_engine.last_input = RESET_COMMAND
    game_engine.last_received_input = RESET_COMMAND
    game_engine.reset_current_mission()
    game_engine.remember_input(RESET_COMMAND, game_engine.last_action, True)
    sync_legacy_state()
    await broadcast_state()
    return build_state({"letra": RESET_COMMAND, "valor": RESET_COMMAND})


reset_demo_state_on_startup()


@app.get("/slots")
async def receive_slots(
    s0: str = Query(default=""),
    s1: str = Query(default=""),
    s2: str = Query(default=""),
    s3: str = Query(default=""),
) -> JSONResponse:
    """Receive the current state of 4 RFID readers simultaneously.
    Send empty string for a slot with no block. Called continuously by the Arduino."""
    game_engine.process_slots([s0, s1, s2, s3])
    sync_legacy_state()
    await broadcast_state()
    return JSONResponse(content=build_state())


@app.get("/arcade")
async def arcade_button() -> JSONResponse:
    """Physical arcade button pressed. Calls /arcade from the Arduino microswitch.
    Currently triggers ENTER (validate answer). Change here for future exercises."""
    return await handle_nfc_value("ENTER")


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


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
