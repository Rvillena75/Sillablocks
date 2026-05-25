import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BackendClient, type StateConnection } from "./api/backendClient";
import type { GameProgress, MissionState, ShopState } from "./api/types";
import { GameHeader } from "./components/GameHeader";
import { MissionView } from "./components/MissionView";
import { VillageView } from "./components/VillageView";

export function App() {
  const client = useMemo(() => new BackendClient(), []);
  const socketRef = useRef<StateConnection | null>(null);
  const [view, setView] = useState<"mission" | "village">("mission");
  const [mission, setMission] = useState<MissionState | null>(null);
  const [progress, setProgress] = useState<GameProgress | null>(null);
  const [shop, setShop] = useState<ShopState | null>(null);
  const [socketStatus, setSocketStatus] = useState("conectando");
  const [villageMessage, setVillageMessage] = useState("");
  const [appError, setAppError] = useState("");

  const refreshProgress = useCallback(async () => {
    const [nextProgress, nextShop] = await Promise.all([client.getProgress(), client.getShop()]);
    setProgress(nextProgress);
    setShop(nextShop);
  }, [client]);

  const refreshAll = useCallback(async () => {
    const [nextMission, nextProgress, nextShop] = await Promise.all([
      client.getBuffer(),
      client.getProgress(),
      client.getShop(),
    ]);
    setMission(nextMission);
    setProgress(nextProgress);
    setShop(nextShop);
  }, [client]);

  useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  useEffect(() => {
    let reconnectTimer = 0;

    function handleState(state: MissionState) {
      setMission(state);
      setAppError("");
      if ((state.events || []).length > 0) {
        void refreshProgress();
      }
    }

    function connectSocket() {
      const socket = client.connectStateSocket(
        handleState,
        (status) => {
          if (socketRef.current !== socket) {
            return;
          }
          setSocketStatus(status);
          if (status === "reconectando") {
            window.clearTimeout(reconnectTimer);
            reconnectTimer = window.setTimeout(connectSocket, 1200);
          }
        },
      );
      socketRef.current = socket;
    }

    connectSocket();

    return () => {
      window.clearTimeout(reconnectTimer);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [client, refreshProgress]);

  async function runAction(action: () => Promise<void>, fallbackMessage: string) {
    try {
      await action();
      setAppError("");
    } catch (error) {
      const message = error instanceof Error ? error.message : fallbackMessage;
      setAppError(message || fallbackMessage);
      setVillageMessage(message || fallbackMessage);
      await refreshAll().catch(() => undefined);
    }
  }

  async function sendInput(value: string) {
    await runAction(async () => {
      const next = await client.sendInput(value);
      setMission(next);
      if ((next.events || []).length > 0 || value === "RESET_TODO") {
        await refreshProgress();
      }
    }, "No se pudo enviar ese cubo.");
  }

  async function buyItem(itemId: string) {
    await runAction(async () => {
      const result = await client.buy(itemId);
      setVillageMessage(result.message);
      setProgress(result.progress);
      await refreshProgress();
    }, "No se pudo comprar esa decoración.");
  }

  async function placeDecoration(itemId: string, x: number, y: number) {
    await runAction(async () => {
      const result = await client.placeDecoration(itemId, x, y);
      setVillageMessage(result.message);
      setProgress(result.progress);
      await refreshProgress();
    }, "No se pudo colocar esa decoración.");
  }

  async function moveDecoration(decorationId: string, x: number, y: number) {
    await runAction(async () => {
      const result = await client.moveDecoration(decorationId, x, y);
      setVillageMessage(result.message);
      setProgress(result.progress);
      await refreshProgress();
    }, "No se pudo mover esa decoración.");
  }

  async function removeDecoration(decorationId: string) {
    await runAction(async () => {
      const result = await client.removeDecoration(decorationId);
      setVillageMessage(result.message);
      setProgress(result.progress);
      await refreshProgress();
    }, "No se pudo guardar esa decoración.");
  }

  async function selectMission(missionId: string) {
    await runAction(async () => {
      const next = await client.selectMission(missionId);
      setMission(next);
      await refreshProgress();
      setView("mission");
    }, "No se pudo abrir esa misión.");
  }

  if (!mission) {
    return <div className="app-loading">Abriendo el bosque de Lumo...</div>;
  }

  return (
    <div className="storybook-app">
      {appError && (
        <div className="app-error" role="status">
          {appError}
        </div>
      )}
      <GameHeader
        progress={progress}
        socketStatus={socketStatus}
        view={view}
        onOpenMission={() => setView("mission")}
        onOpenVillage={() => setView("village")}
      />
      <div className={`app-view ${view === "mission" ? "active" : ""}`} aria-hidden={view !== "mission"}>
        <MissionView state={mission} socketStatus={socketStatus} onSend={(value) => void sendInput(value)} />
      </div>
      <div className={`app-view ${view === "village" ? "active" : ""}`} aria-hidden={view !== "village"}>
        <VillageView
          mission={mission}
          progress={progress}
          shop={shop}
          message={villageMessage}
          onStartMission={(missionId) => void selectMission(missionId)}
          onBuy={(itemId) => void buyItem(itemId)}
          onPlace={(itemId, x, y) => void placeDecoration(itemId, x, y)}
          onMove={(decorationId, x, y) => void moveDecoration(decorationId, x, y)}
          onRemove={(decorationId) => void removeDecoration(decorationId)}
        />
      </div>
    </div>
  );
}
