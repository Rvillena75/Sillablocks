import Phaser from "phaser";
import type { BackendClient } from "../api/backendClient";
import type { MissionState } from "../api/types";
import type { BootData } from "./BootScene";
import { DebugOverlay } from "./DebugOverlay";
import { MissionEventPlayer } from "../systems/MissionEventPlayer";

const COMMANDS = ["BORRAR", "RESET", "ENTER", "SIGUIENTE"];

export class MissionScene extends Phaser.Scene {
  private client!: BackendClient;
  private state!: MissionState;
  private debug!: DebugOverlay;
  private eventPlayer = new MissionEventPlayer();
  private socket: WebSocket | null = null;
  private blockGroup!: Phaser.GameObjects.Group;
  private buttonGroup!: Phaser.GameObjects.Group;
  private promptText!: Phaser.GameObjects.Text;
  private feedbackText!: Phaser.GameObjects.Text;
  private progressBar!: Phaser.GameObjects.Rectangle;
  private targetText!: Phaser.GameObjects.Text;
  private lumo!: Phaser.GameObjects.Arc;
  private lanternGlow!: Phaser.GameObjects.Arc;

  constructor() {
    super("MissionScene");
  }

  create(data: BootData): void {
    this.client = data.client;
    this.state = data.mission;
    this.blockGroup = this.add.group();
    this.buttonGroup = this.add.group();

    this.createScene();
    this.debug = new DebugOverlay(this);
    this.connectSocket();
    this.render(this.state);
  }

  shutdown(): void {
    this.socket?.close();
    this.socket = null;
  }

  private createScene(): void {
    const { width, height } = this.scale;
    this.add.rectangle(width / 2, height / 2, width, height, 0x102421);
    this.add.rectangle(width / 2, height - 105, width, 210, 0x2f4a36);
    this.add.ellipse(width / 2, height - 90, width * 0.72, 130, 0xb88a4a, 0.7);

    for (let i = 0; i < 7; i += 1) {
      const x = 130 + i * 175;
      this.add.triangle(x, height - 210, 0, 140, 58, 0, 116, 140, 0x173629);
      this.add.rectangle(x, height - 130, 18, 92, 0x583b2a);
    }

    this.lanternGlow = this.add.circle(width * 0.72, height * 0.43, 46, 0xf6d36a, 0.12);
    this.add.rectangle(width * 0.72, height * 0.5, 14, 115, 0x4d3427);
    this.add.rectangle(width * 0.72, height * 0.42, 64, 72, 0x2b241e);
    this.add.circle(width * 0.72, height * 0.42, 22, 0xf2c94c, 0.25);

    this.lumo = this.add.circle(width * 0.22, height * 0.44, 36, 0xf4f0d8);
    this.add.circle(width * 0.21, height * 0.435, 4, 0x102421);
    this.add.circle(width * 0.23, height * 0.435, 4, 0x102421);

    this.promptText = this.add.text(width / 2, height - 205, "", {
      align: "center",
      color: "#fff8dd",
      fontFamily: "Arial",
      fontSize: "30px",
      fontStyle: "bold",
      wordWrap: { width: width * 0.76 },
    }).setOrigin(0.5, 0);

    this.targetText = this.add.text(width / 2, height - 250, "", {
      align: "center",
      color: "#e6ffd7",
      fontFamily: "Arial",
      fontSize: "20px",
    }).setOrigin(0.5, 0);

    this.add.rectangle(width / 2, height - 78, 420, 18, 0x0b1916);
    this.progressBar = this.add.rectangle(width / 2 - 210, height - 78, 0, 18, 0x8bdc70);
    this.progressBar.setOrigin(0, 0.5);

    this.feedbackText = this.add.text(width / 2, height - 52, "", {
      align: "center",
      color: "#f4f0d8",
      fontFamily: "Arial",
      fontSize: "22px",
      wordWrap: { width: width * 0.7 },
    }).setOrigin(0.5, 0);

    this.add.text(width - 150, 24, "Aldea", {
      backgroundColor: "#243f36",
      color: "#f4f0d8",
      fontFamily: "Arial",
      fontSize: "18px",
      padding: { x: 16, y: 10 },
    })
      .setInteractive({ useHandCursor: true })
      .on("pointerdown", () => this.scene.start("VillageScene", { client: this.client, mission: this.state }));
  }

  private connectSocket(): void {
    this.socket = this.client.connectStateSocket(
      (state) => {
        this.eventPlayer.play(state.events);
        this.render(state);
      },
      (status) => {
        this.debug.setSocketStatus(status);
        this.debug.render(this.state);
        if (status === "reconectando") {
          window.setTimeout(() => this.connectSocket(), 1200);
        }
      },
    );
  }

  private render(state: MissionState): void {
    this.state = state;
    const { width, height } = this.scale;
    this.promptText.setText(state.prompt);
    this.targetText.setText(`Mision ${state.mission_number}/${state.total_missions} · ${state.zone}`);
    this.feedbackText.setText(state.feedback);
    this.progressBar.width = Math.round(420 * (state.progress_percent / 100));
    this.lanternGlow.setAlpha(state.status === "success" || state.status === "demo_complete" ? 0.8 : 0.14);
    this.lumo.setScale(state.status === "success" ? 1.12 : 1);

    this.blockGroup.clear(true, true);
    const startX = width / 2 - (state.target_blocks.length * 74) / 2 + 37;
    state.current_blocks.forEach((block, index) => {
      const x = startX + index * 74;
      const y = height - 128;
      const tile = this.add.rectangle(x, y, 58, 58, 0xf7d88b).setStrokeStyle(3, 0x5c3c1d);
      const label = this.add.text(x, y, block, {
        color: "#332214",
        fontFamily: "Arial",
        fontSize: "26px",
        fontStyle: "bold",
      }).setOrigin(0.5);
      this.blockGroup.addMultiple([tile, label]);
    });

    this.renderButtons();
    this.debug.render(state);
  }

  private renderButtons(): void {
    this.buttonGroup.clear(true, true);
    const values = [...this.state.available_blocks, ...COMMANDS];
    values.forEach((value, index) => {
      const x = 80 + (index % 5) * 86;
      const y = this.scale.height - 18 - Math.floor(index / 5) * 48;
      const bg = this.add.rectangle(x, y, 72, 36, COMMANDS.includes(value) ? 0x46535c : 0xf7d88b)
        .setInteractive({ useHandCursor: true })
        .on("pointerdown", async () => {
          const next = await this.client.sendInput(value);
          this.eventPlayer.play(next.events);
          this.render(next);
        });
      const text = this.add.text(x, y, value, {
        color: COMMANDS.includes(value) ? "#ffffff" : "#332214",
        fontFamily: "Arial",
        fontSize: "16px",
        fontStyle: "bold",
      }).setOrigin(0.5);
      this.buttonGroup.addMultiple([bg, text]);
    });
  }
}
