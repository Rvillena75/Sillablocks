import type { GameProgress } from "../api/types";
import { ResourcePill } from "./ResourcePill";

interface GameHeaderProps {
  progress: GameProgress | null;
  socketStatus: string;
  view: "mission" | "village";
  onOpenMission: () => void;
  onOpenVillage: () => void;
}

export function GameHeader({ progress, socketStatus, view, onOpenMission, onOpenVillage }: GameHeaderProps) {
  return (
    <header className="game-header">
      <div className="brand-lockup">
        <div className="brand-mark">S</div>
        <div>
          <p>El Mundo de las Palabras Perdidas</p>
          <h1>SilaBlocks</h1>
        </div>
      </div>
      <div className="header-actions">
        <ResourcePill label="Lúmenes" value={progress?.lumens ?? 0} tone="gold" />
        <ResourcePill label="Fragmentos" value={progress?.fragments ?? progress?.map_fragments ?? 0} tone="blue" />
        <span className={`connection-pill ${socketStatus}`}>{socketStatus}</span>
        <button className="soft-tab" type="button" aria-pressed={view === "mission"} onClick={onOpenMission}>
          Misión
        </button>
        <button className="soft-tab primary" type="button" aria-pressed={view === "village"} onClick={onOpenVillage}>
          Aldea
        </button>
      </div>
    </header>
  );
}

