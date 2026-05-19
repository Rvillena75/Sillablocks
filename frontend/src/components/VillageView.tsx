import { useMemo, useState } from "react";
import type { GameProgress, MissionState, PlacedDecoration, ShopItem, ShopState } from "../api/types";
import { ActionButton } from "./ActionButton";

interface VillageViewProps {
  mission: MissionState | null;
  progress: GameProgress | null;
  shop: ShopState | null;
  message: string;
  onStartMission: (missionId: string) => void;
  onBuy: (itemId: string) => void;
  onPlace: (itemId: string, x: number, y: number) => void;
  onMove: (decorationId: string, x: number, y: number) => void;
  onRemove: (decorationId: string) => void;
}

interface FunctionalVillageObject {
  id: string;
  missionId: string;
  name: string;
  description: string;
  restoredDescription: string;
  lockedDescription: string;
  objective: string;
  rewardLabel: string;
  restorationKeys: string[];
  x: number;
  y: number;
  kind: "lantern" | "path" | "sign" | "house" | "bridge";
}

type FunctionalObjectState = "locked" | "damaged" | "restored";

const functionalVillageObjects: FunctionalVillageObject[] = [
  {
    id: "lantern_01",
    missionId: "m001",
    name: "Farol perdido",
    description: "Este farol olvidó su palabra. Devuélvele la luz con tus cubos.",
    restoredDescription: "El farol vuelve a iluminar la entrada del bosque.",
    lockedDescription: "El farol espera al inicio de la aventura.",
    objective: "Forma la palabra MAMA",
    rewardLabel: "+10 Lúmenes",
    restorationKeys: ["Farol del Bosque"],
    x: 28,
    y: 56,
    kind: "lantern",
  },
  {
    id: "path_01",
    missionId: "m002",
    name: "Camino dormido",
    description: "El camino de madera perdió sus pasos. Ayuda a Lumo a abrirlo.",
    restoredDescription: "El camino ya deja avanzar a Lumo por la aldea.",
    lockedDescription: "Primero enciende el farol para ver por dónde avanzar.",
    objective: "Forma la palabra PAPA",
    rewardLabel: "+10 Lúmenes",
    restorationKeys: ["Camino de Madera"],
    x: 42,
    y: 71,
    kind: "path",
  },
  {
    id: "sign_01",
    missionId: "m003",
    name: "Señal sin voz",
    description: "La señal quedó rota y no recuerda qué lugar indica.",
    restoredDescription: "La señal vuelve a mostrar el camino hacia el pueblo.",
    lockedDescription: "El camino debe despertar antes de llegar a esta señal.",
    objective: "Forma la palabra CASA",
    rewardLabel: "+12 Lúmenes",
    restorationKeys: ["Señal del Pueblo"],
    x: 55,
    y: 49,
    kind: "sign",
  },
  {
    id: "house_01",
    missionId: "m004",
    name: "Casa de la plaza",
    description: "La casa cerró sus ventanas porque la plaza perdió su palabra.",
    restoredDescription: "La plaza vuelve a tener un rincón donde reunirse.",
    lockedDescription: "La señal del pueblo debe quedar lista antes de abrir esta casa.",
    objective: "Forma la palabra MESA",
    rewardLabel: "+12 Lúmenes",
    restorationKeys: ["Mesa de la Plaza"],
    x: 70,
    y: 62,
    kind: "house",
  },
  {
    id: "bridge_01",
    missionId: "m005",
    name: "Puente de la ruta",
    description: "El puente perdió sus primeras pisadas y la ruta quedó incompleta.",
    restoredDescription: "El puente abre la primera ruta de exploración.",
    lockedDescription: "La plaza debe volver a brillar antes de cruzar este puente.",
    objective: "Forma la palabra BOTA",
    rewardLabel: "+14 Lúmenes",
    restorationKeys: ["Ruta del Explorador"],
    x: 83,
    y: 76,
    kind: "bridge",
  },
];

const itemGlyphs: Record<string, string> = {
  small_lantern: "✦",
  glowing_tree: "✿",
  restored_sign: "➜",
  decorated_house: "▰",
  path_to_village: "╋",
  restored_bridge: "◌",
};

const stateLabels: Record<FunctionalObjectState, string> = {
  locked: "Bloqueado",
  damaged: "Necesita ayuda",
  restored: "Restaurado",
};

export function VillageView({
  mission,
  progress,
  shop,
  message,
  onStartMission,
  onBuy,
  onPlace,
  onMove,
  onRemove,
}: VillageViewProps) {
  const [shopOpen, setShopOpen] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [placingItem, setPlacingItem] = useState<string | null>(null);
  const [movingDecoration, setMovingDecoration] = useState<string | null>(null);
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null);
  const inventory = useMemo(() => shop?.items ?? [], [shop]);
  const nextObject = nextMissionObject(progress, mission);
  const selectedObject = functionalVillageObjects.find((object) => object.id === selectedObjectId)
    ?? nextObject
    ?? functionalVillageObjects[0];
  const selectedState = objectState(selectedObject, progress, mission);
  const currentInstruction = movingDecoration
    ? "Toca un nuevo lugar para moverla."
    : placingItem
      ? "Toca un espacio libre para colocar la decoración."
      : nextObject
        ? `Siguiente misión: ${nextObject.name}`
        : "Primera aventura restaurada.";

  function handleVillageClick(event: React.MouseEvent<HTMLDivElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = Math.round(((event.clientX - rect.left) / rect.width) * 100);
    const y = Math.round(((event.clientY - rect.top) / rect.height) * 100);
    if (movingDecoration) {
      onMove(movingDecoration, x, y);
      setMovingDecoration(null);
      return;
    }
    if (placingItem) {
      onPlace(placingItem, x, y);
      setPlacingItem(null);
    }
  }

  function startPlacement(itemId: string) {
    setEditMode(true);
    setMovingDecoration(null);
    setPlacingItem(itemId);
  }

  function startMove(decorationId: string) {
    setEditMode(true);
    setPlacingItem(null);
    setMovingDecoration(decorationId);
  }

  return (
    <main className="village-screen">
      <section className={`village-canvas parchment-panel ${editMode ? "is-editing" : ""}`} onClick={handleVillageClick}>
        <div className="village-sky" />
        <div className="village-hill back" />
        <div className="village-hill front" />
        <div className="village-path" />
        <p className="village-guide">{currentInstruction}</p>

        {functionalVillageObjects.map((object) => {
          const state = objectState(object, progress, mission);
          return (
            <button
              key={object.id}
              className={`functional-village-object ${object.kind} ${state} ${selectedObject.id === object.id ? "selected" : ""}`}
              type="button"
              style={{ left: `${object.x}%`, top: `${object.y}%` }}
              aria-label={`${object.name}: ${stateLabels[state]}`}
              onClick={(event) => {
                event.stopPropagation();
                setSelectedObjectId(object.id);
              }}
            >
              <span className="functional-object-art" />
              <span className="functional-object-badge">{stateLabels[state]}</span>
            </button>
          );
        })}

        {(progress?.placed_decorations ?? []).map((decoration) => (
          <PlacedDecorationMarker
            key={decoration.id}
            decoration={decoration}
            editMode={editMode}
            onMove={() => startMove(decoration.id)}
            onRemove={() => onRemove(decoration.id)}
          />
        ))}

        <VillageMissionCard object={selectedObject} state={selectedState} onStartMission={onStartMission} />
      </section>

      <aside className={`shop-panel parchment-panel ${shopOpen ? "open" : ""}`}>
        <div className="shop-panel-header">
          <div>
            <p className="panel-eyebrow">Aldea editable</p>
            <h2>Decoraciones</h2>
          </div>
          <button className="shop-toggle" type="button" onClick={() => setShopOpen((value) => !value)}>
            {shopOpen ? "Ocultar" : "Abrir"}
          </button>
        </div>
        {shopOpen && (
          <>
            <div className="edit-mode-row">
              <ActionButton variant={editMode ? "primary" : "soft"} onClick={() => setEditMode((value) => !value)}>
                {editMode ? "Salir de edición" : "Modo edición"}
              </ActionButton>
              {(placingItem || movingDecoration) && (
                <ActionButton
                  variant="soft"
                  onClick={() => {
                    setPlacingItem(null);
                    setMovingDecoration(null);
                  }}
                >
                  Cancelar
                </ActionButton>
              )}
            </div>
            <p className="shop-message">{message || "Compra, coloca y mueve objetos sin cambiar la misión."}</p>
            <div className="shop-list">
              {inventory.map((item) => (
                <ShopCard
                  key={item.item_id}
                  item={item}
                  onBuy={() => onBuy(item.item_id)}
                  onPlace={() => startPlacement(item.item_id)}
                />
              ))}
            </div>
          </>
        )}
      </aside>
    </main>
  );
}

function VillageMissionCard({
  object,
  state,
  onStartMission,
}: {
  object: FunctionalVillageObject;
  state: FunctionalObjectState;
  onStartMission: (missionId: string) => void;
}) {
  const text = state === "restored"
    ? object.restoredDescription
    : state === "locked"
      ? object.lockedDescription
      : object.description;

  return (
    <article className={`village-mission-card ${state}`}>
      <p className="panel-eyebrow">{stateLabels[state]}</p>
      <h2>{object.name}</h2>
      <p>{text}</p>
      <div className="village-mission-meta">
        <span>{object.objective}</span>
        <strong>{object.rewardLabel}</strong>
      </div>
      <ActionButton variant="primary" onClick={() => onStartMission(object.missionId)} disabled={state !== "damaged"}>
        {state === "restored" ? "Restaurado" : "Comenzar"}
      </ActionButton>
    </article>
  );
}

function PlacedDecorationMarker({
  decoration,
  editMode,
  onMove,
  onRemove,
}: {
  decoration: PlacedDecoration;
  editMode: boolean;
  onMove: () => void;
  onRemove: () => void;
}) {
  return (
    <div
      className={`placed-decoration ${editMode ? "editable" : ""}`}
      style={{ left: `${decoration.position.x}%`, top: `${decoration.position.y}%` }}
      onClick={(event) => event.stopPropagation()}
    >
      <span>{itemGlyphs[decoration.item_id] ?? "✦"}</span>
      {editMode && (
        <div className="decoration-actions">
          <button type="button" onClick={onMove}>Mover</button>
          <button type="button" onClick={onRemove}>Guardar</button>
        </div>
      )}
    </div>
  );
}

function ShopCard({ item, onBuy, onPlace }: { item: ShopItem; onBuy: () => void; onPlace: () => void }) {
  const canPlace = item.available_to_place > 0;
  return (
    <article className="shop-card">
      <span className="shop-glyph">{itemGlyphs[item.item_id] ?? "✦"}</span>
      <div>
        <h3>{item.name}</h3>
        <p>{item.description}</p>
        <small>
          {item.cost.lumens} Lúmenes · {item.available_to_place} guardadas
        </small>
      </div>
      <div className="shop-card-actions">
        {canPlace && <ActionButton onClick={onPlace}>Colocar</ActionButton>}
        <ActionButton variant={item.affordable ? "primary" : "soft"} onClick={onBuy} disabled={!item.affordable}>
          {item.purchased ? "Comprar más" : item.affordable ? "Comprar" : "Reunir"}
        </ActionButton>
      </div>
    </article>
  );
}

function progressMissions(progress: GameProgress | null, mission: MissionState | null): Set<string> {
  return new Set([
    ...(progress?.completed_missions ?? []),
    ...(mission?.completed_mission_ids ?? []),
  ]);
}

function progressRestorations(progress: GameProgress | null): Set<string> {
  return new Set(progress?.restored_items ?? []);
}

function nextMissionObject(progress: GameProgress | null, mission: MissionState | null): FunctionalVillageObject | null {
  const completed = progressMissions(progress, mission);
  const currentMissionId = mission?.mission_id;
  const currentObject = functionalVillageObjects.find((object) => object.missionId === currentMissionId);
  if (currentObject && !completed.has(currentObject.missionId)) {
    return currentObject;
  }
  return functionalVillageObjects.find((object) => !completed.has(object.missionId)) ?? null;
}

function objectState(
  object: FunctionalVillageObject,
  progress: GameProgress | null,
  mission: MissionState | null,
): FunctionalObjectState {
  const completed = progressMissions(progress, mission);
  const restored = progressRestorations(progress);
  if (completed.has(object.missionId) || object.restorationKeys.some((key) => restored.has(key))) {
    return "restored";
  }
  return nextMissionObject(progress, mission)?.missionId === object.missionId ? "damaged" : "locked";
}
