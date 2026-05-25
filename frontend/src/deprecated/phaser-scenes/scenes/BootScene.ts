import Phaser from "phaser";
import { BackendClient } from "../../../api/backendClient";
import type { GameProgress, MissionState, ShopState } from "../../../api/types";

export interface BootData {
  client: BackendClient;
  mission: MissionState;
  progress: GameProgress;
  shop: ShopState;
}

export class BootScene extends Phaser.Scene {
  constructor() {
    super("BootScene");
  }

  preload(): void {
    this.load.setPath("/");
  }

  async create(): Promise<void> {
    const client = new BackendClient();
    this.add.text(32, 32, "Conectando con SilaBlocks...", {
      color: "#f4f0d8",
      fontFamily: "Arial",
      fontSize: "28px",
    });

    try {
      const [mission, progress, shop] = await Promise.all([
        client.getBuffer(),
        client.getProgress(),
        client.getShop(),
      ]);
      this.scene.start("MissionScene", { client, mission, progress, shop } satisfies BootData);
    } catch (error) {
      this.add.text(32, 86, "No se pudo contactar FastAPI en localhost:5000.", {
        color: "#ffd2bd",
        fontFamily: "Arial",
        fontSize: "20px",
      });
    }
  }
}
