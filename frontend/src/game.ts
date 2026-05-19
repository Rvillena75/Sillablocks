import Phaser from "phaser";
import { BootScene } from "./scenes/BootScene";
import { MissionScene } from "./scenes/MissionScene";
import { RewardScene } from "./scenes/RewardScene";
import { VillageScene } from "./scenes/VillageScene";

export function createGame(parent: string): Phaser.Game {
  return new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    backgroundColor: "#102421",
    scale: {
      mode: Phaser.Scale.RESIZE,
      width: 1280,
      height: 720,
    },
    scene: [BootScene, MissionScene, RewardScene, VillageScene],
  });
}

