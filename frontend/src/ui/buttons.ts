import Phaser from "phaser";

export function addTextButton(
  scene: Phaser.Scene,
  x: number,
  y: number,
  label: string,
  onClick: () => void,
): Phaser.GameObjects.Container {
  const bg = scene.add.rectangle(0, 0, 128, 42, 0xf7d88b).setStrokeStyle(2, 0x5c3c1d);
  const text = scene.add.text(0, 0, label, {
    color: "#332214",
    fontFamily: "Arial",
    fontSize: "18px",
    fontStyle: "bold",
  }).setOrigin(0.5);
  const container = scene.add.container(x, y, [bg, text]);
  bg.setInteractive({ useHandCursor: true }).on("pointerdown", onClick);
  return container;
}

