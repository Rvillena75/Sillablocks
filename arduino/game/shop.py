from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .progress import GameProgress


@dataclass(frozen=True)
class ShopItem:
    item_id: str
    name: str
    description: str
    category: str
    cost_lumens: int = 0
    cost_fragments: int = 0
    restores_item: str | None = None
    unlocks_zone: str | None = None

    def as_dict(self, progress: GameProgress | None = None) -> dict[str, Any]:
        purchased = False
        affordable = False
        if progress is not None:
            purchased = self.item_id in progress.purchased_items
            affordable = (
                progress.lumens >= self.cost_lumens
                and progress.fragments >= self.cost_fragments
            )

        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "cost": {
                "lumens": self.cost_lumens,
                "fragments": self.cost_fragments,
            },
            "purchased": purchased,
            "affordable": affordable and not purchased,
            "restores_item": self.restores_item,
            "unlocks_zone": self.unlocks_zone,
        }


@dataclass(frozen=True)
class PurchaseResult:
    ok: bool
    code: str
    message: str
    item: ShopItem | None
    events: list[dict[str, Any]]
    status_code: int = 200


SHOP_ITEMS: tuple[ShopItem, ...] = (
    ShopItem(
        item_id="small_lantern",
        name="Farol pequeno",
        description="Agrega una luz suave a la aldea.",
        category="decoration",
        cost_lumens=8,
        restores_item="small_lantern",
    ),
    ShopItem(
        item_id="glowing_tree",
        name="Arbol luminoso",
        description="Devuelve brillo y color al bosque cercano.",
        category="decoration",
        cost_lumens=10,
        restores_item="glowing_tree",
    ),
    ShopItem(
        item_id="restored_sign",
        name="Senal restaurada",
        description="Marca el camino para nuevas aventuras.",
        category="decoration",
        cost_lumens=12,
        restores_item="restored_sign",
    ),
    ShopItem(
        item_id="decorated_house",
        name="Casa decorada",
        description="Personaliza una casa de la aldea.",
        category="decoration",
        cost_lumens=15,
        restores_item="decorated_house",
    ),
    ShopItem(
        item_id="path_to_village",
        name="Abrir camino al Pueblo",
        description="Abre una ruta hacia el Pueblo de los Mensajes.",
        category="unlock",
        cost_fragments=1,
        restores_item="path_to_village",
        unlocks_zone="village",
    ),
    ShopItem(
        item_id="restored_bridge",
        name="Restaurar puente",
        description="Reconstruye un puente para cruzar a nuevas zonas.",
        category="unlock",
        cost_fragments=2,
        restores_item="restored_bridge",
        unlocks_zone="bridge_path",
    ),
)

SHOP_ITEM_BY_ID = {item.item_id: item for item in SHOP_ITEMS}


def build_shop_payload(progress: GameProgress) -> dict[str, Any]:
    return {
        "ok": True,
        "resources": {
            "lumens": progress.lumens,
            "fragments": progress.fragments,
        },
        "items": [item.as_dict(progress) for item in SHOP_ITEMS],
    }


def buy_shop_item(progress: GameProgress, item_id: str) -> PurchaseResult:
    cleaned_item_id = item_id.strip()
    item = SHOP_ITEM_BY_ID.get(cleaned_item_id)
    if item is None:
        return PurchaseResult(
            ok=False,
            code="unknown_item",
            message="No encontramos esa mejora.",
            item=None,
            events=[],
            status_code=404,
        )

    if item.item_id in progress.purchased_items:
        return PurchaseResult(
            ok=False,
            code="already_purchased",
            message="Esa mejora ya esta en la aldea.",
            item=item,
            events=[],
            status_code=409,
        )

    if progress.lumens < item.cost_lumens or progress.fragments < item.cost_fragments:
        return PurchaseResult(
            ok=False,
            code="not_enough_resources",
            message="Aun faltan recursos para esa mejora.",
            item=item,
            events=[],
            status_code=400,
        )

    progress.lumens -= item.cost_lumens
    progress.fragments -= item.cost_fragments
    progress.mark_item_purchased(item.item_id)

    events: list[dict[str, Any]] = [
        {
            "type": "item_purchased",
            "item_id": item.item_id,
            "name": item.name,
            "spent": {
                "lumens": item.cost_lumens,
                "fragments": item.cost_fragments,
            },
        }
    ]

    if item.restores_item is not None:
        progress.mark_item_restored(item.restores_item)
        events.append(
            {
                "type": "village_restored",
                "item_id": item.restores_item,
                "name": item.name,
            }
        )

    if item.unlocks_zone is not None:
        progress.unlock_zone(item.unlocks_zone)
        events.append(
            {
                "type": "zone_unlocked",
                "zone_id": item.unlocks_zone,
            }
        )

    return PurchaseResult(
        ok=True,
        code="purchased",
        message="Mejora agregada a la aldea.",
        item=item,
        events=events,
    )
