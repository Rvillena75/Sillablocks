import Phaser from "phaser";
import type { BackendClient } from "../../../api/backendClient";
import type { GameProgress, MissionState, ShopState } from "../../../api/types";

interface VillageData {
  client: BackendClient;
  mission: MissionState;
}

export class VillageScene extends Phaser.Scene {
  private client!: BackendClient;
  private mission!: MissionState;
  private progress: GameProgress | null = null;
  private shop: ShopState | null = null;

  constructor() {
    super("VillageScene");
  }

  async create(data: VillageData): Promise<void> {
    this.client = data.client;
    this.mission = data.mission;
    await this.loadVillage();
    this.render();
  }

  private async loadVillage(): Promise<void> {
    const [progress, shop] = await Promise.all([
      this.client.getProgress(),
      this.client.getShop(),
    ]);
    this.progress = progress;
    this.shop = shop;
  }

  private render(): void {
    const { width, height } = this.scale;
    this.add.rectangle(width / 2, height / 2, width, height, 0x19342d);
    this.add.rectangle(width / 2, height - 130, width * 0.78, 180, 0x3f614b);
    this.add.text(width / 2, 40, "Aldea de Lumo", {
      color: "#fff8dd",
      fontFamily: "Arial",
      fontSize: "38px",
      fontStyle: "bold",
    }).setOrigin(0.5);

    this.add.text(40, 98, `Lumenes: ${this.progress?.lumens ?? 0} · Fragmentos: ${this.progress?.fragments ?? 0}`, {
      color: "#d7f7e4",
      fontFamily: "Arial",
      fontSize: "22px",
    });

    const items = this.shop?.items.slice(0, 6) ?? [];
    items.forEach((item, index) => {
      const x = 120 + index * 180;
      const y = 190;
      this.add.rectangle(x, y, 150, 96, item.affordable ? 0xf7d88b : 0x46535c);
      this.add.text(x, y - 24, item.name, {
        align: "center",
        color: item.affordable ? "#332214" : "#ffffff",
        fontFamily: "Arial",
        fontSize: "15px",
        wordWrap: { width: 130 },
      }).setOrigin(0.5);
      this.add.text(x, y + 24, `${item.cost.lumens} L`, {
        color: item.affordable ? "#332214" : "#ffffff",
        fontFamily: "Arial",
        fontSize: "16px",
      }).setOrigin(0.5);
    });

    this.add.text(width / 2, height - 54, "Volver a mision", {
      backgroundColor: "#243f36",
      color: "#f4f0d8",
      fontFamily: "Arial",
      fontSize: "20px",
      padding: { x: 18, y: 12 },
    })
      .setOrigin(0.5)
      .setInteractive({ useHandCursor: true })
      .on("pointerdown", () => this.scene.start("MissionScene", { client: this.client, mission: this.mission }));
  }
}
