import type { MissionState } from "../api/types";
import { CubeTray } from "./CubeTray";
import { DebugPanel } from "./DebugPanel";
import { MissionCard } from "./MissionCard";
import { PhaserStage } from "./PhaserStage";

interface MissionViewProps {
  state: MissionState;
  socketStatus: string;
  onSend: (value: string) => void;
}

export function MissionView({ state, socketStatus, onSend }: MissionViewProps) {
  return (
    <main className="mission-screen">
      <section className="scene-frame">
        <PhaserStage state={state} />
      </section>
      <MissionCard state={state} onDelete={() => onSend("BORRAR")} onEnter={() => onSend("ENTER")} />
      <CubeTray state={state} onSend={onSend} />
      <DebugPanel state={state} socketStatus={socketStatus} onSend={onSend} />
    </main>
  );
}

