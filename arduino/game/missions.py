from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Mission:
    mission_id: str
    prompt: str
    target_blocks: tuple[str, ...]
    accepted_answers: tuple[str, ...]
    available_blocks: tuple[str, ...]
    zone: str
    skill: str
    restoration: str
    reward_lumens: int = 10

    def as_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "prompt": self.prompt,
            "target_blocks": list(self.target_blocks),
            "accepted_answers": list(self.accepted_answers),
            "available_blocks": list(self.available_blocks),
            "zone": self.zone,
            "skill": self.skill,
            "restoration": self.restoration,
            "reward_lumens": self.reward_lumens,
        }


MISSIONS: list[Mission] = [
    Mission(
        mission_id="m001",
        prompt="Ayuda a Lumo a encender el farol perdido.",
        target_blocks=("M", "A", "M", "A"),
        accepted_answers=("MAMA", "MAMÁ"),
        available_blocks=("M", "A", "P", "S"),
        zone="Bosque de las Sílabas",
        skill="letras individuales",
        restoration="Farol del Bosque",
        reward_lumens=10,
    ),
    Mission(
        mission_id="m002",
        prompt="Ayuda a Lumo a abrir el camino de madera.",
        target_blocks=("P", "A", "P", "A"),
        accepted_answers=("PAPA", "PAPÁ"),
        available_blocks=("P", "A", "M", "S"),
        zone="Bosque de las Sílabas",
        skill="letras individuales",
        restoration="Camino de Madera",
        reward_lumens=10,
    ),
    Mission(
        mission_id="m003",
        prompt="Ayuda a Lumo a devolver una señal al pueblo.",
        target_blocks=("C", "A", "S", "A"),
        accepted_answers=("CASA",),
        available_blocks=("C", "A", "S", "M"),
        zone="Pueblo de los Mensajes",
        skill="letras individuales",
        restoration="Señal del Pueblo",
        reward_lumens=12,
    ),
    Mission(
        mission_id="m004",
        prompt="Ayuda a Lumo a restaurar la mesa de la plaza.",
        target_blocks=("M", "E", "S", "A"),
        accepted_answers=("MESA",),
        available_blocks=("M", "E", "S", "A"),
        zone="Pueblo de los Mensajes",
        skill="letras individuales",
        restoration="Mesa de la Plaza",
        reward_lumens=12,
    ),
    Mission(
        mission_id="m005",
        prompt="Ayuda a Lumo a completar la primera ruta.",
        target_blocks=("B", "O", "T", "A"),
        accepted_answers=("BOTA",),
        available_blocks=("B", "O", "T", "A"),
        zone="Camino de las Palabras",
        skill="letras individuales",
        restoration="Ruta del Explorador",
        reward_lumens=14,
    ),
]

FEEDBACK_EMPTY = "Escanea un cubo para comenzar."
FEEDBACK_IN_PROGRESS = "Vas bien. Falta una parte."
FEEDBACK_SUCCESS_TEMPLATE = "Muy bien. Reconstruiste la palabra {target_text}."
FEEDBACK_SUCCESS = FEEDBACK_SUCCESS_TEMPLATE.format(target_text="MAMA")
FEEDBACK_TRY_AGAIN = "Casi. Prueba otra combinación."
FEEDBACK_KEEP_TRYING = "Sigue probando con los cubos."
FEEDBACK_WRONG_BLOCK = "Casi. Revisa el último cubo y prueba otra combinación."
FEEDBACK_NEXT_BLOCKED = "Primero completa esta palabra. Luego avanzamos."
FEEDBACK_DEMO_COMPLETE = "Muy bien. Completaste todas las misiones."
FEEDBACK_FIRST_MISSION = "Ya estás en la primera misión."
