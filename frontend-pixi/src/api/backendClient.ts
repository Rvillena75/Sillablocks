import type { GameProgress, MissionState } from "./types";

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

  async sendInput(value: string): Promise<MissionState> {
    return this.getJson<MissionState>(`/nfc?letra=${encodeURIComponent(value)}`);
  }

  connectStateSocket(onMessage: (state: MissionState) => void, onStatus?: (status: string) => void): WebSocket {
    const socketBaseUrl = this.baseUrl.replace(/^https:/, "wss:").replace(/^http:/, "ws:");
    const socket = new WebSocket(`${socketBaseUrl}/ws`);
    socket.addEventListener("open", () => onStatus?.("conectado"));
    socket.addEventListener("message", (event) => onMessage(JSON.parse(event.data) as MissionState));
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

