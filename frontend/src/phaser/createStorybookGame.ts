import Phaser from "phaser";
import { StorybookScene } from "./StorybookScene";

export function createStorybookGame(parent: HTMLElement): Phaser.Game {
  return new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    backgroundColor: "#14382F",
    transparent: false,
    scale: {
      mode: Phaser.Scale.RESIZE,
      width: parent.clientWidth || 900,
      height: parent.clientHeight || 560,
    },
    render: {
      antialias: true,
      pixelArt: false,
    },
    scene: [StorybookScene],
  });
}

