import { useState } from "react";
import type { MissionState } from "../api/types";
import { ActionButton } from "./ActionButton";

interface DebugPanelProps {
  state: MissionState;
  socketStatus: string;
  onSend: (value: string) => void;
}

export function DebugPanel({ state, socketStatus, onSend }: DebugPanelProps) {
  const [open, setOpen] = useState(false);

  return (
    <section className={`debug-drawer ${open ? "open" : ""}`}>
      <button className="debug-toggle" type="button" onClick={() => setOpen((value) => !value)}>
        {open ? "Ocultar debug" : "Debug"}
      </button>
      {open && (
        <div className="debug-content parchment-panel">
          <div className="debug-actions">
            <ActionButton onClick={() => onSend("RESET")}>Reset misión</ActionButton>
            <ActionButton onClick={() => onSend("ANTERIOR")}>Anterior</ActionButton>
            <ActionButton onClick={() => onSend("SIGUIENTE")}>Siguiente</ActionButton>
            <ActionButton variant="danger" onClick={() => onSend("RESET_TODO")}>Reset todo</ActionButton>
          </div>
          <dl>
            <div><dt>WebSocket</dt><dd>{socketStatus}</dd></div>
            <div><dt>Último input</dt><dd>{state.last_received_input ?? "-"}</dd></div>
            <div><dt>Bloques</dt><dd>{JSON.stringify(state.current_blocks)}</dd></div>
            <div><dt>Misión</dt><dd>{state.mission_id}</dd></div>
            <div><dt>Estado</dt><dd>{state.status}</dd></div>
          </dl>
        </div>
      )}
    </section>
  );
}

