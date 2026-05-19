import type { MissionEvent } from "../api/types";
import { EventBus, Events } from "./EventBus";

export class MissionEventPlayer {
  play(events: MissionEvent[] = []): void {
    for (const event of events) {
      if (event.type === "reward_granted") {
        EventBus.emit(Events.rewardGranted, event);
      }
    }
  }
}

