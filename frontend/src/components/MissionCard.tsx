import type { MissionState } from "../api/types";
import { ActionButton } from "./ActionButton";

interface MissionCardProps {
  state: MissionState;
  onDelete: () => void;
  onEnter: () => void;
}

export function MissionCard({ state, onDelete, onEnter }: MissionCardProps) {
  return (
    <section className="mission-card parchment-panel">
      <div className="mission-kicker">
        <span>Misión {state.mission_number}/{state.total_missions}</span>
        <span>{state.skill}</span>
      </div>
      <h2>{state.prompt}</h2>
      <p className={`feedback-line ${state.status}`}>{state.feedback}</p>
      <div className="word-slots" aria-label="Palabra objetivo">
        {state.target_blocks.map((_, index) => (
          <span key={index} className={state.current_blocks[index] ? "filled" : ""}>
            {state.current_blocks[index] ?? ""}
          </span>
        ))}
      </div>
      <div className="progress-shell">
        <div style={{ width: `${state.progress_percent}%` }} />
      </div>
      <div className="mission-actions">
        <ActionButton variant="soft" onClick={onDelete}>Borrar</ActionButton>
        <ActionButton variant="primary" onClick={onEnter}>Probar</ActionButton>
      </div>
    </section>
  );
}

