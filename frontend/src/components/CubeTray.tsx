import type { MissionState } from "../api/types";

interface CubeTrayProps {
  state: MissionState;
  onSend: (value: string) => void;
}

export function CubeTray({ state, onSend }: CubeTrayProps) {
  return (
    <aside className="cube-tray parchment-panel">
      <p className="panel-eyebrow">Bandeja de cubos mágicos</p>
      <div className="cube-buttons">
        {state.available_blocks.map((block) => (
          <button key={block} className="cube-button" type="button" onClick={() => onSend(block)}>
            {block}
          </button>
        ))}
      </div>
      <p className="tray-hint">Elige cubos o escanéalos con la base física.</p>
    </aside>
  );
}

