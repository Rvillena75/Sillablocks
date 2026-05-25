import type { BuyResponse, DecorationResponse, GameProgress, MissionState, ShopState } from "./types";
import { localDemoState } from "../game/state/localDemoState";

const configuredBaseUrl = import.meta.env.VITE_SILABLOCKS_API_URL as string | undefined;

export interface StateConnection {
  close: () => void;
}

class BackendHttpError extends Error {}

export class BackendClient {
  readonly baseUrl: string;
  private localDemoMode = false;

  constructor(baseUrl = configuredBaseUrl || window.location.origin) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async getBuffer(): Promise<MissionState> {
    return this.getJson<MissionState>("/buffer", () => localDemoState.getBuffer());
  }

  async getProgress(): Promise<GameProgress> {
    return this.getJson<GameProgress>("/progress", () => localDemoState.getProgress());
  }

  async getShop(): Promise<ShopState> {
    return this.getJson<ShopState>("/shop", () => localDemoState.getShop());
  }

  async sendInput(value: string): Promise<MissionState> {
    return this.getJson<MissionState>(
      `/nfc?letra=${encodeURIComponent(value)}`,
      () => localDemoState.sendInput(value),
    );
  }

  async buy(itemId: string): Promise<BuyResponse> {
    return this.postJson<BuyResponse>(
      "/buy",
      { item_id: itemId },
      () => localDemoState.buy(itemId),
    );
  }

  async placeDecoration(itemId: string, x: number, y: number): Promise<DecorationResponse> {
    return this.postJson<DecorationResponse>(
      "/decorations/place",
      { item_id: itemId, x, y },
      () => localDemoState.placeDecoration(itemId, x, y),
    );
  }

  async moveDecoration(decorationId: string, x: number, y: number): Promise<DecorationResponse> {
    return this.postJson<DecorationResponse>(
      `/decorations/${encodeURIComponent(decorationId)}`,
      { x, y },
      () => localDemoState.moveDecoration(decorationId, x, y),
      "PATCH",
    );
  }

  async removeDecoration(decorationId: string): Promise<DecorationResponse> {
    return this.deleteJson<DecorationResponse>(
      `/decorations/${encodeURIComponent(decorationId)}`,
      () => localDemoState.removeDecoration(decorationId),
    );
  }

  async selectMission(missionId: string): Promise<MissionState> {
    return this.postJson<MissionState>(
      "/mission/select",
      { mission_id: missionId },
      () => localDemoState.selectMission(missionId),
    );
  }

  connectStateSocket(onMessage: (state: MissionState) => void, onStatus?: (status: string) => void): StateConnection {
    if (this.localDemoMode) {
      onStatus?.("modo local");
      const unsubscribe = localDemoState.subscribe(onMessage);
      return { close: unsubscribe };
    }

    const socketBaseUrl = this.baseUrl
      .replace(/^https:/, "wss:")
      .replace(/^http:/, "ws:");
    const socket = new WebSocket(`${socketBaseUrl}/ws`);
    let closedByClient = false;
    let unsubscribeLocal: (() => void) | null = null;

    const switchToLocalDemo = () => {
      if (closedByClient || unsubscribeLocal) {
        return;
      }
      this.localDemoMode = true;
      onStatus?.("modo local");
      unsubscribeLocal = localDemoState.subscribe(onMessage);
    };

    socket.addEventListener("open", () => onStatus?.("conectado"));
    socket.addEventListener("message", (event) => {
      onMessage(JSON.parse(event.data) as MissionState);
    });
    socket.addEventListener("close", switchToLocalDemo);
    socket.addEventListener("error", switchToLocalDemo);

    return {
      close: () => {
        closedByClient = true;
        unsubscribeLocal?.();
        socket.close();
      },
    };
  }

  private async getJson<T>(path: string, localFallback: () => T): Promise<T> {
    if (this.localDemoMode) {
      return localFallback();
    }
    try {
      const response = await fetch(`${this.baseUrl}${path}`);
      if (!response.ok) {
        throw new BackendHttpError(`Backend request failed: ${path}`);
      }
      return await response.json() as T;
    } catch (error) {
      return this.fallbackOrThrow(error, localFallback);
    }
  }

  private async postJson<T>(
    path: string,
    payload: object,
    localFallback: () => T,
    method = "POST",
  ): Promise<T> {
    if (this.localDemoMode) {
      return localFallback();
    }
    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null) as { message?: string } | null;
        throw new BackendHttpError(errorPayload?.message || `Backend request failed: ${path} (${response.status})`);
      }
      return await response.json() as T;
    } catch (error) {
      return this.fallbackOrThrow(error, localFallback);
    }
  }

  private async deleteJson<T>(path: string, localFallback: () => T): Promise<T> {
    if (this.localDemoMode) {
      return localFallback();
    }
    try {
      const response = await fetch(`${this.baseUrl}${path}`, { method: "DELETE" });
      if (!response.ok) {
        throw new BackendHttpError(`Backend request failed: ${path} (${response.status})`);
      }
      return await response.json() as T;
    } catch (error) {
      return this.fallbackOrThrow(error, localFallback);
    }
  }

  private fallbackOrThrow<T>(error: unknown, localFallback: () => T): T {
    void error;
    this.localDemoMode = true;
    return localFallback();
  }
}
