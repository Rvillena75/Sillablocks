import Phaser from "phaser";

export class RewardScene extends Phaser.Scene {
  constructor() {
    super("RewardScene");
  }

  create(): void {
    const { width, height } = this.scale;
    this.add.rectangle(width / 2, height / 2, width, height, 0x1c3028);
    this.add.text(width / 2, height / 2 - 40, "Recompensa recibida", {
      color: "#f4f0d8",
      fontFamily: "Arial",
      fontSize: "38px",
      fontStyle: "bold",
    }).setOrigin(0.5);
    this.add.text(width / 2, height / 2 + 20, "Esta escena queda lista para animar Lumenes y restauraciones.", {
      color: "#d7f7e4",
      fontFamily: "Arial",
      fontSize: "20px",
    }).setOrigin(0.5);
  }
}

