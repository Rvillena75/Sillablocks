import Phaser from "phaser";

export function addHeading(scene: Phaser.Scene, x: number, y: number, value: string): Phaser.GameObjects.Text {
  return scene.add.text(x, y, value, {
    color: "#fff8dd",
    fontFamily: "Arial",
    fontSize: "34px",
    fontStyle: "bold",
  });
}

