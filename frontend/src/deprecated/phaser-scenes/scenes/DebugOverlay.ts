import Phaser from "phaser";
import type { MissionState } from "../../../api/types";

export class DebugOverlay {
  private panel: Phaser.GameObjects.Text;
  private socketStatus = "conectando";

  constructor(scene: Phaser.Scene) {
    this.panel = scene.add.text(20, 20, "", {
      backgroundColor: "rgba(13, 27, 24, 0.78)",
      color: "#d7f7e4",
      fontFamily: "Consolas, monospace",
      fontSize: "14px",
      lineSpacing: 4,
      padding: { x: 12, y: 10 },
    });
    this.panel.setDepth(100);
  }

  setSocketStatus(status: string): void {
    this.socketStatus = status;
  }

  render(state: MissionState): void {
    this.panel.setText([
      `ws: ${this.socketStatus}`,
      `input: ${state.last_received_input ?? "-"}`,
      `bloques: ${JSON.stringify(state.current_blocks)}`,
      `texto: ${state.current_text || "-"}`,
      `mision: ${state.mission_id}`,
      `estado: ${state.status}`,
      `siguiente: ${state.expected_next_block ?? "-"}`,
      `recursos: ${state.lumens} L / ${state.map_fragments} F`,
    ]);
  }
}
