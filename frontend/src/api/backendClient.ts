import type { BuyResponse, DecorationResponse, GameProgress, MissionState, ShopState } from "./types";

const configuredBaseUrl = import.meta.env.VITE_SILABLOCKS_API_URL as string | undefined;

export class BackendClient {
  readonly baseUrl: string;

  constructor(baseUrl = configuredBaseUrl || window.location.origin) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getBuffer(): Promise<MissionState> {
    return this.getJson<MissionState>("/buffer");
  }

  async getProgress(): Promise<GameProgress> {
    return this.getJson<GameProgress>("/progress");
  }

  async getShop(): Promise<ShopState> {
    return this.getJson<ShopState>("/shop");
  }

  async sendInput(value: string): Promise<MissionState> {
    return this.getJson<MissionState>(`/nfc?letra=${encodeURIComponent(value)}`);
  }

  async buy(itemId: string): Promise<BuyResponse> {
    const response = await fetch(`${this.baseUrl}/buy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId }),
    });
    if (!response.ok) {
      throw new Error(`Backend request failed: /buy (${response.status})`);
    }
    return response.json() as Promise<BuyResponse>;
  }

  async placeDecoration(itemId: string, x: number, y: number): Promise<DecorationResponse> {
    const response = await fetch(`${this.baseUrl}/decorations/place`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: itemId, x, y }),
    });
    if (!response.ok) {
      throw new Error(`Backend request failed: /decorations/place (${response.status})`);
    }
    return response.json() as Promise<DecorationResponse>;
  }

  async moveDecoration(decorationId: string, x: number, y: number): Promise<DecorationResponse> {
    const response = await fetch(`${this.baseUrl}/decorations/${encodeURIComponent(decorationId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ x, y }),
    });
    if (!response.ok) {
      throw new Error(`Backend request failed: /decorations/${decorationId} (${response.status})`);
    }
    return response.json() as Promise<DecorationResponse>;
  }

  async removeDecoration(decorationId: string): Promise<DecorationResponse> {
    const response = await fetch(`${this.baseUrl}/decorations/${encodeURIComponent(decorationId)}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error(`Backend request failed: /decorations/${decorationId} (${response.status})`);
    }
    return response.json() as Promise<DecorationResponse>;
  }

  async selectMission(missionId: string): Promise<MissionState> {
    const response = await fetch(`${this.baseUrl}/mission/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mission_id: missionId }),
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => null) as { message?: string } | null;
      throw new Error(payload?.message || `Backend request failed: /mission/select (${response.status})`);
    }
    return response.json() as Promise<MissionState>;
  }

  connectStateSocket(onMessage: (state: MissionState) => void, onStatus?: (status: string) => void): WebSocket {
    const socketBaseUrl = this.baseUrl
      .replace(/^https:/, "wss:")
      .replace(/^http:/, "ws:");
    const socket = new WebSocket(`${socketBaseUrl}/ws`);

    socket.addEventListener("open", () => onStatus?.("conectado"));
    socket.addEventListener("message", (event) => {
      onMessage(JSON.parse(event.data) as MissionState);
    });
    socket.addEventListener("close", () => onStatus?.("reconectando"));
    socket.addEventListener("error", () => onStatus?.("revisar"));

    return socket;
  }

  private async getJson<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`);
    if (!response.ok) {
      throw new Error(`Backend request failed: ${path}`);
    }
    return response.json() as Promise<T>;
  }
}
