import Phaser from "phaser";

export const EventBus = new Phaser.Events.EventEmitter();

export const Events = {
  stateChanged: "state-changed",
  socketStatus: "socket-status",
  rewardGranted: "reward-granted",
} as const;

