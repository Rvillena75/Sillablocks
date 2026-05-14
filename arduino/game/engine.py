from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .buffer import BlockBuffer
from .missions import (
    FEEDBACK_DEMO_COMPLETE,
    FEEDBACK_EMPTY,
    FEEDBACK_FIRST_MISSION,
    FEEDBACK_IN_PROGRESS,
    FEEDBACK_NEXT_BLOCKED,
    FEEDBACK_SUCCESS_TEMPLATE,
    FEEDBACK_TRY_AGAIN,
    FEEDBACK_WRONG_BLOCK,
    MISSIONS,
    Mission,
)


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


@dataclass
class ProcessedInput:
    value: str
    action: str
    accepted: bool

    @property
    def ignored(self) -> bool:
        return not self.accepted


@dataclass
class GameEngine:
    missions: list[Mission] = field(default_factory=lambda: list(MISSIONS))
    buffer: BlockBuffer = field(default_factory=BlockBuffer)
    current_mission_index: int = 0
    completed_mission_ids: set[str] = field(default_factory=set)
    rewarded_mission_ids: set[str] = field(default_factory=set)
    restored_items: list[str] = field(default_factory=list)
    recent_inputs: list[dict[str, Any]] = field(default_factory=list)
    lumens: int = 0
    map_fragments: int = 0
    last_input: str | None = None
    last_received_input: str | None = None
    last_ignored_input: str | None = None
    last_action: str = "init"
    status: str = "idle"
    feedback: str = FEEDBACK_EMPTY

    @property
    def current_blocks(self) -> list[str]:
        return self.buffer.blocks

    def reset_runtime(self) -> None:
        self.buffer.clear()
        self.current_mission_index = 0
        self.completed_mission_ids.clear()
        self.rewarded_mission_ids.clear()
        self.restored_items.clear()
        self.recent_inputs.clear()
        self.lumens = 0
        self.map_fragments = 0
        self.last_input = None
        self.last_received_input = None
        self.last_ignored_input = None
        self.last_action = "init"
        self.status = "idle"
        self.feedback = FEEDBACK_EMPTY

    def normalize_input(self, value: str | None) -> str:
        if value is None:
            return ""
        return value.strip().upper()

    def current_text(self) -> str:
        return self.buffer.text()

    def current_mission(self) -> Mission:
        return self.missions[self.current_mission_index]

    def target_text(self) -> str:
        return self.current_mission().accepted_answers[0]

    def mission_number(self) -> int:
        return self.current_mission_index + 1

    def total_missions(self) -> int:
        return len(self.missions)

    def is_last_mission(self) -> bool:
        return self.current_mission_index == len(self.missions) - 1

    def is_prefix_of_target(self, blocks: list[str] | None = None) -> bool:
        checked_blocks = self.current_blocks if blocks is None else blocks
        target_blocks = list(self.current_mission().target_blocks)
        if len(checked_blocks) > len(target_blocks):
            return False
        return checked_blocks == target_blocks[: len(checked_blocks)]

    def is_exact_target_blocks(self, blocks: list[str] | None = None) -> bool:
        checked_blocks = self.current_blocks if blocks is None else blocks
        return checked_blocks == list(self.current_mission().target_blocks)

    def correct_prefix_count(self, blocks: list[str] | None = None) -> int:
        checked_blocks = self.current_blocks if blocks is None else blocks
        target_blocks = list(self.current_mission().target_blocks)
        count = 0
        for index, block in enumerate(checked_blocks):
            if index >= len(target_blocks) or block != target_blocks[index]:
                break
            count += 1
        return count

    def progress_percent(self) -> int:
        target_count = max(len(self.current_mission().target_blocks), 1)
        return round((self.correct_prefix_count() / target_count) * 100)

    def expected_next_block(self) -> str | None:
        count = self.correct_prefix_count()
        target_blocks = self.current_mission().target_blocks
        if count < len(target_blocks):
            return target_blocks[count]
        return None

    def remember_input(self, value: str, action: str, accepted: bool) -> None:
        self.recent_inputs.append(
            {
                "value": value,
                "action": action,
                "accepted": accepted,
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )
        del self.recent_inputs[:-8]

    def complete_current_mission(self) -> None:
        mission = self.current_mission()
        self.completed_mission_ids.add(mission.mission_id)
        if mission.mission_id in self.rewarded_mission_ids:
            return

        self.rewarded_mission_ids.add(mission.mission_id)
        self.lumens += mission.reward_lumens
        self.restored_items.append(mission.restoration)
        if len(self.rewarded_mission_ids) in {3, 5}:
            self.map_fragments += 1

    def evaluate_game_state(self, validate_now: bool = False) -> None:
        if not self.current_blocks:
            self.status = "idle"
            self.feedback = FEEDBACK_EMPTY
            return

        if self.is_exact_target_blocks():
            self.complete_current_mission()
            self.status = "success"
            self.feedback = FEEDBACK_SUCCESS_TEMPLATE.format(target_text=self.target_text())
            return

        if not self.is_prefix_of_target():
            self.status = "try_again"
            self.feedback = FEEDBACK_TRY_AGAIN if validate_now else FEEDBACK_WRONG_BLOCK
            return

        if validate_now:
            self.status = "try_again"
            self.feedback = FEEDBACK_TRY_AGAIN
            return

        self.status = "in_progress"
        self.feedback = FEEDBACK_IN_PROGRESS

    def reset_current_mission(self) -> None:
        self.completed_mission_ids.discard(self.current_mission().mission_id)
        self.buffer.clear()
        self.last_ignored_input = None
        self.last_action = "reset"
        self.evaluate_game_state()

    def reset_all(self) -> None:
        self.current_mission_index = 0
        self.completed_mission_ids.clear()
        self.rewarded_mission_ids.clear()
        self.restored_items.clear()
        self.buffer.clear()
        self.lumens = 0
        self.map_fragments = 0
        self.last_ignored_input = None
        self.last_action = "reset_all"
        self.evaluate_game_state()

    def go_to_next_mission(self) -> bool:
        if self.status != "success":
            self.last_action = "next_blocked"
            self.feedback = FEEDBACK_NEXT_BLOCKED
            return False

        self.complete_current_mission()
        if self.is_last_mission():
            self.last_action = "demo_complete"
            self.status = "demo_complete"
            self.feedback = FEEDBACK_DEMO_COMPLETE
            return True

        self.current_mission_index += 1
        self.buffer.clear()
        self.last_ignored_input = None
        self.last_action = "next"
        self.evaluate_game_state()
        return True

    def go_to_previous_mission(self) -> bool:
        if self.current_mission_index == 0:
            self.last_action = "previous_blocked"
            self.feedback = FEEDBACK_FIRST_MISSION
            return False

        self.current_mission_index -= 1
        self.buffer.clear()
        self.last_ignored_input = None
        self.last_action = "previous"
        self.evaluate_game_state()
        return True

    def process_input(self, raw_value: str) -> ProcessedInput:
        value = self.normalize_input(raw_value)
        self.last_received_input = value
        accepted = True

        if value in DELETE_COMMANDS:
            self.buffer.delete_last()
            self.last_action = "delete"
            self.last_input = value
            self.evaluate_game_state()
        elif value == RESET_COMMAND:
            self.last_input = value
            self.reset_current_mission()
        elif value == RESET_ALL_COMMAND:
            self.last_input = value
            self.reset_all()
        elif value == ENTER_COMMAND:
            self.last_action = "validate"
            self.last_input = value
            self.evaluate_game_state(validate_now=True)
        elif value == NEXT_COMMAND:
            self.last_input = value
            accepted = self.go_to_next_mission()
        elif value == PREVIOUS_COMMAND:
            self.last_input = value
            accepted = self.go_to_previous_mission()
        elif self.status in {"success", "demo_complete"}:
            self.last_action = "ignored_after_success"
            self.last_ignored_input = value
            accepted = False
        else:
            self.buffer.append(value)
            self.last_action = "append"
            self.last_input = value
            self.evaluate_game_state()

        self.remember_input(value, self.last_action, accepted)
        return ProcessedInput(value=value, action=self.last_action, accepted=accepted)

    def reward_state(self) -> dict[str, Any]:
        return {
            "lumens": self.lumens,
            "map_fragments": self.map_fragments,
            "restored_items": list(self.restored_items),
            "rewarded_mission_ids": sorted(self.rewarded_mission_ids),
        }

    def build_state(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.current_text()
        correct_count = self.correct_prefix_count()
        mission = self.current_mission()
        progress = 100 if self.status in {"success", "demo_complete"} else self.progress_percent()
        state: dict[str, Any] = {
            "ok": True,
            "buffer": text,
            "texto": text,
            "bloques": self.buffer.copy(),
            "current_blocks": self.buffer.copy(),
            "current_text": text,
            "last_input": self.last_input,
            "ultimo_input": self.last_input,
            "last_received_input": self.last_received_input,
            "ultimo_recibido": self.last_received_input,
            "last_ignored_input": self.last_ignored_input,
            "ultimo_ignorado": self.last_ignored_input,
            "recent_inputs": list(self.recent_inputs),
            "accion": self.last_action,
            "action": self.last_action,
            "mission_id": mission.mission_id,
            "mission_number": self.mission_number(),
            "total_missions": self.total_missions(),
            "completed_missions": len(self.completed_mission_ids),
            "completed_mission_ids": sorted(self.completed_mission_ids),
            "is_last_mission": self.is_last_mission(),
            "is_demo_complete": self.status == "demo_complete",
            "current_mission_index": self.current_mission_index,
            "prompt": mission.prompt,
            "target_text": self.target_text(),
            "target_blocks": list(mission.target_blocks),
            "accepted_answers": list(mission.accepted_answers),
            "available_blocks": list(mission.available_blocks),
            "missions": [item.as_dict() for item in self.missions],
            "correct_prefix_count": correct_count,
            "target_block_count": len(mission.target_blocks),
            "progress_percent": progress,
            "overall_progress_percent": round(
                (len(self.completed_mission_ids) / self.total_missions()) * 100
            ),
            "expected_next_block": self.expected_next_block(),
            "has_block_mismatch": bool(self.current_blocks) and not self.is_prefix_of_target(),
            "status": self.status,
            "feedback": self.feedback,
            "mission": mission.as_dict(),
            "zone": mission.zone,
            "skill": mission.skill,
            "restoration": mission.restoration,
            "rewards": self.reward_state(),
            "lumens": self.lumens,
            "map_fragments": self.map_fragments,
            "restored_items": list(self.restored_items),
        }
        if extra:
            state.update(extra)
        return state
