import type { GameProgress, ShopItem, ShopState as ShopPayload } from "../api/types";

export class ShopStateModel {
  progress: GameProgress | null = null;
  shop: ShopPayload | null = null;

  update(progress: GameProgress, shop: ShopPayload): void {
    this.progress = progress;
    this.shop = shop;
  }

  affordableItems(): ShopItem[] {
    return this.shop?.items.filter((item) => item.affordable) ?? [];
  }
}

