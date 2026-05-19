export type MissionStatus = "idle" | "in_progress" | "try_again" | "success" | "demo_complete";

export type MissionEvent =
  | {
      type: "mission_completed";
      mission_id: string;
      target_text: string;
    }
  | {
      type: "reward_granted";
      mission_id: string;
      lumens: number;
      fragments: number;
    }
  | {
      type: "scene_restored";
      mission_id: string;
      item: string;
    }
  | {
      type: "item_purchased";
      item_id: string;
      name: string;
      spent: ResourceCost;
    }
  | {
      type: "decoration_placed" | "decoration_moved" | "decoration_removed";
      decoration: PlacedDecoration;
    }
  | {
      type: string;
      [key: string]: unknown;
    };

export interface MissionState {
  ok: boolean;
  current_blocks: string[];
  current_text: string;
  last_input: string | null;
  last_received_input: string | null;
  last_ignored_input: string | null;
  action: string;
  mission_id: string;
  mission_number: number;
  total_missions: number;
  completed_mission_ids: string[];
  prompt: string;
  target_text: string;
  target_blocks: string[];
  available_blocks: string[];
  status: MissionStatus;
  feedback: string;
  progress_percent: number;
  expected_next_block: string | null;
  zone: string;
  skill: string;
  restoration: string;
  lumens: number;
  map_fragments: number;
  events?: MissionEvent[];
}

export interface GameProgress {
  ok: boolean;
  lumens: number;
  fragments: number;
  map_fragments: number;
  completed_missions: string[];
  purchased_items: string[];
  unlocked_zones: string[];
  restored_items: string[];
  placed_decorations: PlacedDecoration[];
}

export interface ResourceCost {
  lumens: number;
  fragments: number;
}

export interface PlacedDecoration {
  id: string;
  item_id: string;
  position: {
    x: number;
    y: number;
  };
  rotation: number;
  scale: number;
}

