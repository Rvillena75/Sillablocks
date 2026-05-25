import type {
  BuyResponse,
  DecorationResponse,
  GameProgress,
  MissionEvent,
  MissionState,
  PlacedDecoration,
  ResourceCost,
  ShopItem,
  ShopState,
} from "../../api/types";

interface DemoMission {
  mission_id: string;
  prompt: string;
  target_blocks: string[];
  available_blocks: string[];
  zone: string;
  skill: string;
  restoration: string;
  reward_lumens: number;
}

const MISSIONS: DemoMission[] = [
  {
    mission_id: "m001",
    prompt: "Ayuda a Lumo a encender el farol perdido.",
    target_blocks: ["M", "A", "M", "A"],
    available_blocks: ["M", "A", "P", "S"],
    zone: "Bosque de las Silabas",
    skill: "letras individuales",
    restoration: "Farol del Bosque",
    reward_lumens: 10,
  },
  {
    mission_id: "m002",
    prompt: "Ayuda a Lumo a abrir el camino de madera.",
    target_blocks: ["P", "A", "P", "A"],
    available_blocks: ["P", "A", "M", "S"],
    zone: "Bosque de las Silabas",
    skill: "letras individuales",
    restoration: "Camino de Madera",
    reward_lumens: 10,
  },
  {
    mission_id: "m003",
    prompt: "Ayuda a Lumo a devolver una señal al pueblo.",
    target_blocks: ["C", "A", "S", "A"],
    available_blocks: ["C", "A", "S", "M"],
    zone: "Pueblo de los Mensajes",
    skill: "letras individuales",
    restoration: "Señal del Pueblo",
    reward_lumens: 12,
  },
  {
    mission_id: "m004",
    prompt: "Ayuda a Lumo a restaurar la mesa de la plaza.",
    target_blocks: ["M", "E", "S", "A"],
    available_blocks: ["M", "E", "S", "A"],
    zone: "Pueblo de los Mensajes",
    skill: "letras individuales",
    restoration: "Mesa de la Plaza",
    reward_lumens: 12,
  },
  {
    mission_id: "m005",
    prompt: "Ayuda a Lumo a completar la primera ruta.",
    target_blocks: ["B", "O", "T", "A"],
    available_blocks: ["B", "O", "T", "A"],
    zone: "Camino de las Palabras",
    skill: "letras individuales",
    restoration: "Ruta del Explorador",
    reward_lumens: 14,
  },
];

interface DemoShopItem {
  item_id: string;
  name: string;
  description: string;
  category: string;
  cost: ResourceCost;
  restores_item: string | null;
  unlocks_zone: string | null;
}

const SHOP_ITEMS: DemoShopItem[] = [
  {
    item_id: "small_lantern",
    name: "Farol pequeño",
    description: "Una luz suave para decorar el camino.",
    category: "decoration",
    cost: { lumens: 8, fragments: 0 },
    restores_item: null,
    unlocks_zone: null,
  },
  {
    item_id: "glowing_tree",
    name: "Arbol luminoso",
    description: "Un arbol de prueba para la aldea.",
    category: "decoration",
    cost: { lumens: 16, fragments: 0 },
    restores_item: null,
    unlocks_zone: null,
  },
  {
    item_id: "path_to_village",
    name: "Sendero decorado",
    description: "Marca un recorrido dentro de la aldea.",
    category: "decoration",
    cost: { lumens: 10, fragments: 0 },
    restores_item: null,
    unlocks_zone: null,
  },
];

type StateListener = (state: MissionState) => void;

class LocalDemoState {
  private missionIndex = 0;
  private blocks: string[] = [];
  private status: MissionState["status"] = "idle";
  private feedback = "Escanea un cubo para comenzar.";
  private action = "init";
  private lastInput: string | null = null;
  private lastReceivedInput: string | null = null;
  private completedMissionIds = new Set<string>();
  private rewardedMissionIds = new Set<string>();
  private restoredItems: string[] = [];
  private purchasedItems: string[] = [];
  private placedDecorations: PlacedDecoration[] = [];
  private lumens = 0;
  private fragments = 0;
  private listeners = new Set<StateListener>();

  subscribe(listener: StateListener): () => void {
    this.listeners.add(listener);
    listener(this.getBuffer());
    return () => this.listeners.delete(listener);
  }

  getBuffer(): MissionState {
    const mission = this.currentMission();
    const progressPercent = this.status === "success" || this.status === "demo_complete"
      ? 100
      : Math.round((this.correctPrefixCount() / mission.target_blocks.length) * 100);

    return {
      ok: true,
      current_blocks: [...this.blocks],
      current_text: this.blocks.join(""),
      last_input: this.lastInput,
      last_received_input: this.lastReceivedInput,
      last_ignored_input: null,
      action: this.action,
      mission_id: mission.mission_id,
      mission_number: this.missionIndex + 1,
      total_missions: MISSIONS.length,
      completed_mission_ids: [...this.completedMissionIds],
      prompt: mission.prompt,
      target_text: mission.target_blocks.join(""),
      target_blocks: [...mission.target_blocks],
      available_blocks: [...mission.available_blocks],
      status: this.status,
      feedback: this.feedback,
      progress_percent: progressPercent,
      expected_next_block: this.expectedNextBlock(),
      zone: mission.zone,
      skill: mission.skill,
      restoration: mission.restoration,
      lumens: this.lumens,
      map_fragments: this.fragments,
      events: [],
    };
  }

  getProgress(): GameProgress {
    return {
      ok: true,
      lumens: this.lumens,
      fragments: this.fragments,
      map_fragments: this.fragments,
      completed_missions: [...this.completedMissionIds],
      purchased_items: [...this.purchasedItems],
      unlocked_zones: ["forest"],
      restored_items: [...this.restoredItems],
      placed_decorations: this.placedDecorations.map((decoration) => ({ ...decoration })),
    };
  }

  getShop(): ShopState {
    const progress = this.getProgress();
    return {
      ok: true,
      resources: { lumens: progress.lumens, fragments: progress.fragments },
      items: SHOP_ITEMS.map((item) => this.buildShopItem(item)),
    };
  }

  sendInput(rawValue: string): MissionState {
    const value = rawValue.trim().toUpperCase();
    this.lastReceivedInput = value;
    this.lastInput = value;

    if (!value) {
      this.action = "ignored";
      return this.withEvents([]);
    }

    if (["BORRAR", "DELETE", "BACKSPACE"].includes(value)) {
      this.blocks.pop();
      this.action = "delete";
      this.evaluate(false);
      return this.withEvents([]);
    }

    if (value === "RESET") {
      this.blocks = [];
      this.action = "reset";
      this.evaluate(false);
      return this.withEvents([]);
    }

    if (value === "RESET_TODO") {
      this.resetAll();
      return this.withEvents([]);
    }

    if (value === "ANTERIOR") {
      this.missionIndex = Math.max(this.missionIndex - 1, 0);
      this.blocks = [];
      this.action = "previous";
      this.evaluate(false);
      return this.withEvents([]);
    }

    if (value === "SIGUIENTE") {
      return this.nextMission();
    }

    if (value === "ENTER") {
      this.action = "validate";
      this.evaluate(true);
      return this.withEvents(this.completeCurrentMissionIfNeeded());
    }

    if (this.status === "success" || this.status === "demo_complete") {
      this.action = "ignored_after_success";
      return this.withEvents([]);
    }

    this.blocks.push(value);
    this.action = "append";
    this.evaluate(false);
    return this.withEvents(this.completeCurrentMissionIfNeeded());
  }

  selectMission(missionId: string): MissionState {
    const nextIndex = MISSIONS.findIndex((mission) => mission.mission_id === missionId);
    if (nextIndex < 0) {
      throw new Error("Misión no encontrada.");
    }
    const previousMission = nextIndex === 0 ? null : MISSIONS[nextIndex - 1];
    if (previousMission && !this.completedMissionIds.has(previousMission.mission_id)) {
      throw new Error("Primero completa la misión anterior.");
    }
    this.missionIndex = nextIndex;
    this.blocks = [];
    this.action = "select_mission";
    this.evaluate(false);
    return this.withEvents([]);
  }

  buy(itemId: string): BuyResponse {
    const item = SHOP_ITEMS.find((candidate) => candidate.item_id === itemId);
    if (!item) {
      throw new Error("Decoración no encontrada.");
    }
    if (this.lumens < item.cost.lumens || this.fragments < item.cost.fragments) {
      return {
        ok: false,
        code: "insufficient_resources",
        message: "Faltan lúmenes para comprar esta decoración.",
        item: this.buildShopItem(item),
        progress: this.getProgress(),
        events: [],
      };
    }
    this.lumens -= item.cost.lumens;
    this.fragments -= item.cost.fragments;
    this.purchasedItems.push(item.item_id);
    const events: MissionEvent[] = [
      {
        type: "item_purchased",
        item_id: item.item_id,
        name: item.name,
        spent: item.cost,
      },
    ];
    this.notify();
    return {
      ok: true,
      code: "purchased",
      message: `${item.name} guardado en la aldea.`,
      item: this.buildShopItem(item),
      progress: this.getProgress(),
      events,
    };
  }

  placeDecoration(itemId: string, x: number, y: number): DecorationResponse {
    const available = this.ownedCount(itemId) - this.placedCount(itemId);
    if (available <= 0) {
      throw new Error("Compra esa decoración antes de colocarla.");
    }
    const decoration: PlacedDecoration = {
      id: `local_${String(this.placedDecorations.length + 1).padStart(3, "0")}`,
      item_id: itemId,
      position: { x: this.clampPosition(x), y: this.clampPosition(y) },
      rotation: 0,
      scale: 1,
    };
    this.placedDecorations.push(decoration);
    this.notify();
    return this.decorationResponse("Decoración colocada.", decoration, "decoration_placed");
  }

  moveDecoration(decorationId: string, x: number, y: number): DecorationResponse {
    const decoration = this.placedDecorations.find((candidate) => candidate.id === decorationId);
    if (!decoration) {
      throw new Error("Decoración no encontrada.");
    }
    decoration.position = { x: this.clampPosition(x), y: this.clampPosition(y) };
    this.notify();
    return this.decorationResponse("Decoración movida.", decoration, "decoration_moved");
  }

  removeDecoration(decorationId: string): DecorationResponse {
    const decoration = this.placedDecorations.find((candidate) => candidate.id === decorationId) ?? null;
    this.placedDecorations = this.placedDecorations.filter((candidate) => candidate.id !== decorationId);
    this.notify();
    return this.decorationResponse("Decoración guardada.", decoration, "decoration_removed");
  }

  private currentMission(): DemoMission {
    return MISSIONS[this.missionIndex] ?? MISSIONS[0];
  }

  private evaluate(validateNow: boolean): void {
    if (this.blocks.length === 0) {
      this.status = "idle";
      this.feedback = "Escanea un cubo para comenzar.";
      return;
    }

    if (this.isExactTarget()) {
      this.status = "success";
      this.feedback = `Muy bien. Reconstruiste la palabra ${this.currentMission().target_blocks.join("")}.`;
      return;
    }

    if (!this.isPrefixOfTarget()) {
      this.status = "try_again";
      this.feedback = validateNow
        ? "Casi. Prueba otra combinación."
        : "Casi. Revisa el último cubo y prueba otra combinación.";
      return;
    }

    this.status = "in_progress";
    this.feedback = validateNow ? "Falta una parte." : "Vas bien. Falta una parte.";
  }

  private completeCurrentMissionIfNeeded(): MissionEvent[] {
    if (this.status !== "success") {
      return [];
    }

    const mission = this.currentMission();
    if (this.rewardedMissionIds.has(mission.mission_id)) {
      return [];
    }

    this.completedMissionIds.add(mission.mission_id);
    this.rewardedMissionIds.add(mission.mission_id);
    this.lumens += mission.reward_lumens;
    if (!this.restoredItems.includes(mission.restoration)) {
      this.restoredItems.push(mission.restoration);
    }
    const fragments = this.rewardedMissionIds.size === 3 || this.rewardedMissionIds.size === 5 ? 1 : 0;
    this.fragments += fragments;

    return [
      {
        type: "mission_completed",
        mission_id: mission.mission_id,
        target_text: mission.target_blocks.join(""),
      },
      {
        type: "reward_granted",
        mission_id: mission.mission_id,
        lumens: mission.reward_lumens,
        fragments,
      },
      {
        type: "scene_restored",
        mission_id: mission.mission_id,
        item: mission.restoration,
      },
    ];
  }

  private nextMission(): MissionState {
    if (this.status !== "success") {
      this.action = "next_blocked";
      this.feedback = "Primero completa esta palabra. Luego avanzamos.";
      return this.withEvents([]);
    }

    const events = this.completeCurrentMissionIfNeeded();
    if (this.missionIndex >= MISSIONS.length - 1) {
      this.status = "demo_complete";
      this.feedback = "Muy bien. Completaste todas las misiones.";
      return this.withEvents(events);
    }

    this.missionIndex += 1;
    this.blocks = [];
    this.action = "next";
    this.evaluate(false);
    return this.withEvents(events);
  }

  private resetAll(): void {
    this.missionIndex = 0;
    this.blocks = [];
    this.status = "idle";
    this.feedback = "Escanea un cubo para comenzar.";
    this.action = "reset_all";
    this.lastInput = "RESET_TODO";
    this.completedMissionIds.clear();
    this.rewardedMissionIds.clear();
    this.restoredItems = [];
    this.purchasedItems = [];
    this.placedDecorations = [];
    this.lumens = 0;
    this.fragments = 0;
  }

  private withEvents(events: MissionEvent[]): MissionState {
    const state = { ...this.getBuffer(), events };
    this.notify(state);
    return state;
  }

  private notify(state = this.getBuffer()): void {
    this.listeners.forEach((listener) => listener(state));
  }

  private isPrefixOfTarget(): boolean {
    const target = this.currentMission().target_blocks;
    return this.blocks.every((block, index) => block === target[index]);
  }

  private isExactTarget(): boolean {
    const target = this.currentMission().target_blocks;
    return this.blocks.length === target.length && this.isPrefixOfTarget();
  }

  private correctPrefixCount(): number {
    const target = this.currentMission().target_blocks;
    let count = 0;
    for (let index = 0; index < this.blocks.length; index += 1) {
      if (this.blocks[index] !== target[index]) {
        break;
      }
      count += 1;
    }
    return count;
  }

  private expectedNextBlock(): string | null {
    const target = this.currentMission().target_blocks;
    const count = this.correctPrefixCount();
    return count < target.length ? target[count] : null;
  }

  private buildShopItem(item: DemoShopItem): ShopItem {
    const ownedCount = this.ownedCount(item.item_id);
    const placedCount = this.placedCount(item.item_id);
    return {
      ...item,
      purchased: ownedCount > 0,
      affordable: this.lumens >= item.cost.lumens && this.fragments >= item.cost.fragments,
      placed: placedCount > 0,
      owned_count: ownedCount,
      placed_count: placedCount,
      available_to_place: Math.max(ownedCount - placedCount, 0),
    };
  }

  private ownedCount(itemId: string): number {
    return this.purchasedItems.filter((candidate) => candidate === itemId).length;
  }

  private placedCount(itemId: string): number {
    return this.placedDecorations.filter((candidate) => candidate.item_id === itemId).length;
  }

  private clampPosition(value: number): number {
    return Math.max(0, Math.min(100, Math.round(value)));
  }

  private decorationResponse(
    message: string,
    decoration: PlacedDecoration | null,
    type: "decoration_placed" | "decoration_moved" | "decoration_removed",
  ): DecorationResponse {
    return {
      ok: true,
      message,
      decoration,
      progress: this.getProgress(),
      events: decoration ? [{ type, decoration }] : [],
    };
  }
}

export const localDemoState = new LocalDemoState();
