import { useEffect, useRef, useState } from "react";
import Phaser from "phaser";
import type { MissionState } from "../api/types";
import { createStorybookGame } from "../phaser/createStorybookGame";
import { pushMissionState } from "../phaser/sceneBus";

interface PhaserStageProps {
  state: MissionState;
}

export function PhaserStage({ state }: PhaserStageProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const latestStateRef = useRef(state);
  const [ready, setReady] = useState(false);

  latestStateRef.current = state;

  useEffect(() => {
    const host = hostRef.current;
    if (!host || gameRef.current) return;

    let animationFrame = 0;
    const startWhenSized = () => {
      const { width, height } = host.getBoundingClientRect();
      if (width < 120 || height < 120) {
        animationFrame = window.requestAnimationFrame(startWhenSized);
        return;
      }
      gameRef.current = createStorybookGame(host);
      pushMissionState(latestStateRef.current);
      setReady(true);
    };

    const observer = new ResizeObserver(() => {
      if (!gameRef.current) {
        window.cancelAnimationFrame(animationFrame);
        animationFrame = window.requestAnimationFrame(startWhenSized);
      }
    });

    observer.observe(host);
    animationFrame = window.requestAnimationFrame(startWhenSized);

    return () => {
      observer.disconnect();
      window.cancelAnimationFrame(animationFrame);
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  }, []);

  useEffect(() => {
    pushMissionState(state);
  }, [state]);

  return (
    <div className="phaser-stage" ref={hostRef} aria-label="Escena del bosque">
      {!ready && <div className="phaser-stage-fallback" />}
    </div>
  );
}
