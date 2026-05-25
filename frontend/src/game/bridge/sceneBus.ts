import Phaser from "phaser";
import type { MissionState } from "../../api/types";

export const sceneBus = new Phaser.Events.EventEmitter();

export const SceneEvents = {
  stateChanged: "state-changed",
} as const;

let latestMissionState: MissionState | null = null;

export function pushMissionState(state: MissionState): void {
  latestMissionState = state;
  sceneBus.emit(SceneEvents.stateChanged, state);
}

export function getLatestMissionState(): MissionState | null {
  return latestMissionState;
}
