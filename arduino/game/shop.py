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
        owned_count = 0
        placed_count = 0
        affordable = False
        if progress is not None:
            owned_count = progress.purchased_items.count(self.item_id)
            affordable = (
                progress.lumens >= self.cost_lumens
                and progress.fragments >= self.cost_fragments
            )
            placed_count = sum(
                1
                for decoration in progress.placed_decorations
                if decoration.get("item_id") == self.item_id
            )

        available_to_place = max(owned_count - placed_count, 0)
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "cost": {
                "lumens": self.cost_lumens,
                "fragments": self.cost_fragments,
            },
            "purchased": owned_count > 0,
            "affordable": affordable,
            "placed": placed_count > 0,
            "owned_count": owned_count,
            "placed_count": placed_count,
            "available_to_place": available_to_place,
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
        name="Farol de luciernagas",
        description="Decoracion opcional para iluminar un rincon de la aldea.",
        category="decoration",
        cost_lumens=6,
    ),
    ShopItem(
        item_id="glowing_tree",
        name="Flores brillantes",
        description="Parche de flores para decorar caminos y plazas.",
        category="decoration",
        cost_lumens=6,
    ),
    ShopItem(
        item_id="restored_sign",
        name="Cartel pintado",
        description="Un cartel bonito para personalizar la entrada.",
        category="decoration",
        cost_lumens=7,
    ),
    ShopItem(
        item_id="decorated_house",
        name="Banco de plaza",
        description="Asiento decorativo para armar un lugar de descanso.",
        category="decoration",
        cost_lumens=8,
    ),
    ShopItem(
        item_id="path_to_village",
        name="Cerca de madera",
        description="Decoracion para ordenar bordes y senderos.",
        category="decoration",
        cost_lumens=8,
    ),
    ShopItem(
        item_id="restored_bridge",
        name="Fuente pequena",
        description="Adorno central para darle vida a la plaza.",
        category="decoration",
        cost_lumens=10,
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
            message="No encontramos esa decoracion.",
            item=None,
            events=[],
            status_code=404,
        )

    if progress.lumens < item.cost_lumens or progress.fragments < item.cost_fragments:
        return PurchaseResult(
            ok=False,
            code="not_enough_resources",
            message="Aun faltan recursos para esa decoracion.",
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
        message="Decoracion agregada a la aldea.",
        item=item,
        events=events,
    )
