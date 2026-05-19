import {
  Application,
  Assets,
  BlurFilter,
  Container,
  FederatedPointerEvent,
  Graphics,
  Sprite,
  Text,
  Texture,
} from "pixi.js";
import { BackendClient } from "../api/backendClient";
import type { MissionEvent, MissionState } from "../api/types";

const LETTER_COMMANDS = ["BORRAR", "RESET", "ENTER", "SIGUIENTE"];

interface SceneRefs {
  background: Sprite;
  fireflies: Graphics[];
  letterMist: Text[];
  lanternGlow: Graphics;
  lanternLight: Graphics;
  lumo: Container;
  lumoGlow: Graphics;
  missionCard: Container;
  prompt: Text;
  missionMeta: Text;
  feedback: Text;
  progressFill: Graphics;
  cubes: Container;
  buttons: Container;
  resources: Text;
  debug: Text;
  celebration: Graphics;
}

export class SilaPixiGame {
  private app = new Application();
  private client = new BackendClient();
  private state: MissionState | null = null;
  private socket: WebSocket | null = null;
  private socketStatus = "conectando";
  private refs!: SceneRefs;
  private time = 0;

  constructor(private readonly root: HTMLElement) {}

  async init(): Promise<void> {
    await this.app.init({
      resizeTo: this.root,
      antialias: true,
      autoDensity: true,
      backgroundAlpha: 1,
      backgroundColor: 0x14271f,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
    });

    this.root.appendChild(this.app.canvas);
    await this.createScene();
    await this.loadState();
    this.connectSocket();
    this.app.ticker.add((ticker) => this.update(ticker.deltaTime));
    window.addEventListener("resize", () => this.layout());
  }

  private async loadState(): Promise<void> {
    const state = await this.client.getBuffer();
    const progress = await this.client.getProgress();
    this.render({ ...state, lumens: progress.lumens, map_fragments: progress.fragments });
  }

  private connectSocket(): void {
    this.socket = this.client.connectStateSocket(
      (state) => {
        this.playEvents(state.events || []);
        this.render(state);
      },
      (status) => {
        this.socketStatus = status;
        this.renderDebug();
        if (status === "reconectando") {
          window.setTimeout(() => this.connectSocket(), 1200);
        }
      },
    );
  }

  private async createScene(): Promise<void> {
    await Assets.load([]);
    const background = new Sprite(this.createBackgroundTexture());
    this.app.stage.addChild(background);

    const fireflies = Array.from({ length: 18 }, (_, index) => {
      const dot = new Graphics().circle(0, 0, 2 + (index % 3)).fill({ color: 0xffe58b, alpha: 0.72 });
      this.app.stage.addChild(dot);
      return dot;
    });

    const letterMist = ["M", "A", "P", "S", "C", "E"].map((letter) => {
      const text = this.makeText(letter, 46, "#fff1a7", 900);
      text.alpha = 0.24;
      this.app.stage.addChild(text);
      return text;
    });

    const lanternGlow = new Graphics();
    lanternGlow.filters = [new BlurFilter({ strength: 18 })];
    this.app.stage.addChild(lanternGlow);

    const lanternLight = new Graphics();
    this.app.stage.addChild(lanternLight);
    const lumo = this.createLumo();
    const lumoGlow = lumo.getChildByName("lumoGlow") as Graphics;
    this.app.stage.addChild(lumo);

    const missionCard = new Container();
    const prompt = this.makeText("", 30, "#fff7d8", 900);
    const missionMeta = this.makeText("", 16, "#b9f3c4", 800);
    const feedback = this.makeText("", 21, "#f7e9b7", 800);
    const progressFill = new Graphics();
    const cubes = new Container();
    const buttons = new Container();
    const resources = this.makeText("", 18, "#fff1c6", 900);
    const debug = this.makeText("", 13, "#d5ffe4", 600, "Consolas, monospace");
    const celebration = new Graphics();
    celebration.alpha = 0;

    this.app.stage.addChild(missionCard, cubes, buttons, resources, debug, celebration);
    missionCard.addChild(missionMeta, prompt, feedback, progressFill);

    this.refs = {
      background,
      fireflies,
      letterMist,
      lanternGlow,
      lanternLight,
      lumo,
      lumoGlow,
      missionCard,
      prompt,
      missionMeta,
      feedback,
      progressFill,
      cubes,
      buttons,
      resources,
      debug,
      celebration,
    };
    this.layout();
  }

  private layout(): void {
    if (!this.refs) return;
    const width = this.app.screen.width;
    const height = this.app.screen.height;
    this.refs.background.texture = this.createBackgroundTexture();
    this.refs.background.width = width;
    this.refs.background.height = height;

    this.refs.lumo.position.set(width * 0.18, height * 0.47);
    this.drawLantern();
    this.drawMissionCard();
    this.renderButtons();
    this.renderCubes();
    this.renderDebug();
  }

  private render(state: MissionState): void {
    this.state = state;
    const success = state.status === "success" || state.status === "demo_complete";
    this.refs.prompt.text = state.prompt;
    this.refs.feedback.text = state.feedback;
    this.refs.missionMeta.text = `Mision ${state.mission_number}/${state.total_missions} · ${state.zone}`;
    this.refs.resources.text = `${state.lumens} Lumenes · ${state.map_fragments} Fragmentos`;
    this.refs.lanternGlow.alpha = success ? 0.95 : Math.max(0.18, state.progress_percent / 160);
    this.refs.lanternLight.alpha = success ? 1 : Math.max(0.22, state.progress_percent / 130);
    this.refs.lumo.scale.set(success ? 1.08 : 1);
    this.drawProgress();
    this.renderCubes();
    this.renderButtons();
    this.renderDebug();
  }

  private update(delta: number): void {
    this.time += delta / 60;
    const { width, height } = this.app.screen;
    this.refs.fireflies.forEach((dot, index) => {
      const t = this.time * (0.35 + index * 0.02) + index;
      dot.position.set(
        width * (0.08 + ((index * 0.061 + Math.sin(t) * 0.035) % 0.86)),
        height * (0.18 + ((index * 0.089 + Math.cos(t * 0.7) * 0.045) % 0.54)),
      );
      dot.alpha = 0.35 + Math.sin(t * 2.1) * 0.25;
    });

    this.refs.letterMist.forEach((letter, index) => {
      letter.position.set(
        width * (0.25 + index * 0.095),
        height * (0.20 + Math.sin(this.time + index) * 0.04),
      );
      letter.rotation = Math.sin(this.time * 0.7 + index) * 0.08;
    });

    this.refs.lumo.y += Math.sin(this.time * 2.2) * 0.25;
    this.refs.lumoGlow.alpha = 0.22 + Math.sin(this.time * 2.5) * 0.08;
    if (this.refs.celebration.alpha > 0) {
      this.refs.celebration.alpha = Math.max(0, this.refs.celebration.alpha - delta * 0.025);
    }
  }

  private createBackgroundTexture(): Texture {
    const width = Math.max(960, this.root.clientWidth || 1280);
    const height = Math.max(540, this.root.clientHeight || 720);
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return Texture.WHITE;

    const sky = ctx.createLinearGradient(0, 0, 0, height);
    sky.addColorStop(0, "#173f50");
    sky.addColorStop(0.45, "#245c52");
    sky.addColorStop(1, "#143126");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, width, height);

    const glow = ctx.createRadialGradient(width * 0.74, height * 0.25, 20, width * 0.74, height * 0.25, height * 0.45);
    glow.addColorStop(0, "rgba(255,228,130,0.45)");
    glow.addColorStop(0.42, "rgba(255,190,92,0.12)");
    glow.addColorStop(1, "rgba(255,190,92,0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, width, height);

    this.drawHill(ctx, width, height, height * 0.62, "#1d4f3c", 0.018);
    this.drawHill(ctx, width, height, height * 0.70, "#183f32", 0.025);
    this.drawHill(ctx, width, height, height * 0.82, "#25442f", 0.015);

    for (let i = 0; i < 12; i += 1) {
      const x = width * (i / 11);
      const y = height * (0.42 + (i % 3) * 0.045);
      this.drawTree(ctx, x, y, 0.75 + (i % 4) * 0.13);
    }

    const path = ctx.createLinearGradient(0, height * 0.62, 0, height);
    path.addColorStop(0, "#9d7241");
    path.addColorStop(1, "#d7b06e");
    ctx.beginPath();
    ctx.moveTo(width * 0.46, height * 0.58);
    ctx.bezierCurveTo(width * 0.35, height * 0.76, width * 0.35, height, width * 0.20, height);
    ctx.lineTo(width * 0.84, height);
    ctx.bezierCurveTo(width * 0.64, height * 0.86, width * 0.64, height * 0.70, width * 0.54, height * 0.58);
    ctx.closePath();
    ctx.fillStyle = path;
    ctx.fill();

    const mist = ctx.createLinearGradient(0, height * 0.52, 0, height * 0.80);
    mist.addColorStop(0, "rgba(224,244,231,0)");
    mist.addColorStop(0.45, "rgba(224,244,231,0.22)");
    mist.addColorStop(1, "rgba(224,244,231,0)");
    ctx.fillStyle = mist;
    ctx.fillRect(0, height * 0.48, width, height * 0.30);

    return Texture.from(canvas);
  }

  private drawHill(ctx: CanvasRenderingContext2D, width: number, height: number, baseY: number, color: string, wave: number): void {
    ctx.beginPath();
    ctx.moveTo(0, height);
    for (let x = 0; x <= width; x += width / 12) {
      const y = baseY + Math.sin(x * wave) * height * 0.04;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
  }

  private drawTree(ctx: CanvasRenderingContext2D, x: number, y: number, scale: number): void {
    ctx.fillStyle = "#533726";
    ctx.fillRect(x - 8 * scale, y + 58 * scale, 16 * scale, 94 * scale);
    ctx.fillStyle = "#17402f";
    for (let layer = 0; layer < 3; layer += 1) {
      ctx.beginPath();
      ctx.moveTo(x, y + layer * 42 * scale);
      ctx.lineTo(x - (58 - layer * 10) * scale, y + (92 + layer * 26) * scale);
      ctx.lineTo(x + (58 - layer * 10) * scale, y + (92 + layer * 26) * scale);
      ctx.closePath();
      ctx.fill();
    }
  }

  private createLumo(): Container {
    const lumo = new Container();
    const glow = new Graphics().circle(0, 0, 54).fill({ color: 0xfff3a9, alpha: 0.26 });
    glow.name = "lumoGlow";
    glow.filters = [new BlurFilter({ strength: 12 })];
    const body = new Graphics()
      .circle(0, 0, 38)
      .fill(0xfff4c9)
      .circle(-13, -6, 5)
      .fill(0x243126)
      .circle(13, -6, 5)
      .fill(0x243126)
      .roundRect(-16, 12, 32, 8, 6)
      .fill(0xf08b6b);
    const sparkOne = new Graphics().star(-42, -34, 5, 7, 3).fill(0xffef8a);
    const sparkTwo = new Graphics().star(42, -26, 5, 6, 2).fill(0xa8f6bf);
    lumo.addChild(glow, sparkOne, sparkTwo, body);
    return lumo;
  }

  private drawLantern(): void {
    const { width, height } = this.app.screen;
    const x = width * 0.73;
    const y = height * 0.45;
    this.refs.lanternGlow.clear()
      .circle(x, y, 98)
      .fill({ color: 0xffdc74, alpha: 0.55 });
    this.refs.lanternLight.clear()
      .poly([x - 75, y + 38, x + 75, y + 38, x + 130, height, x - 130, height])
      .fill({ color: 0xffdf8a, alpha: 0.18 })
      .roundRect(x - 34, y - 42, 68, 82, 16)
      .fill(0x3d2a1e)
      .roundRect(x - 23, y - 24, 46, 48, 12)
      .fill({ color: 0xffd46a, alpha: 0.72 })
      .rect(x - 6, y + 38, 12, 112)
      .fill(0x4b3325);
  }

  private drawMissionCard(): void {
    const { width, height } = this.app.screen;
    const card = this.refs.missionCard;
    card.removeChildren();
    const bg = new Graphics()
      .roundRect(0, 0, Math.min(740, width * 0.78), 178, 24)
      .fill({ color: 0x10251f, alpha: 0.82 })
      .stroke({ color: 0xf3d98d, width: 2, alpha: 0.35 });
    bg.filters = [new BlurFilter({ strength: 0.6 })];
    card.addChild(bg, this.refs.missionMeta, this.refs.prompt, this.refs.feedback, this.refs.progressFill);
    card.position.set(width / 2 - bg.width / 2, height - 210);
    this.refs.missionMeta.position.set(28, 22);
    this.refs.prompt.position.set(28, 52);
    this.refs.prompt.style.wordWrap = true;
    this.refs.prompt.style.wordWrapWidth = bg.width - 56;
    this.refs.feedback.position.set(28, 126);
    this.refs.feedback.style.wordWrap = true;
    this.refs.feedback.style.wordWrapWidth = bg.width - 56;
    this.drawProgress();
  }

  private drawProgress(): void {
    if (!this.state) return;
    const bgWidth = Math.min(740, this.app.screen.width * 0.78) - 56;
    this.refs.progressFill.clear()
      .roundRect(28, 108, bgWidth, 12, 8)
      .fill({ color: 0x081713, alpha: 0.9 })
      .roundRect(28, 108, Math.max(8, bgWidth * (this.state.progress_percent / 100)), 12, 8)
      .fill(0x9be36b);
  }

  private renderCubes(): void {
    if (!this.state || !this.refs) return;
    this.refs.cubes.removeChildren();
    const { width, height } = this.app.screen;
    const blocks = this.state.current_blocks;
    const target = Math.max(this.state.target_blocks.length, 1);
    const startX = width / 2 - ((target - 1) * 78) / 2;
    for (let index = 0; index < target; index += 1) {
      const x = startX + index * 78;
      const y = height - 282;
      const filled = blocks[index];
      const cube = new Graphics()
        .roundRect(-30, -30, 60, 60, 14)
        .fill(filled ? 0xffd778 : 0xd9e4bc)
        .stroke({ color: filled ? 0x6b441d : 0x819076, width: 3, alpha: 0.85 });
      cube.position.set(x, y);
      const shadow = new Graphics().ellipse(0, 38, 31, 7).fill({ color: 0x132019, alpha: 0.25 });
      shadow.position.set(x, y);
      this.refs.cubes.addChild(shadow, cube);
      if (filled) {
        const label = this.makeText(filled, 30, "#352213", 900);
        label.anchor.set(0.5);
        label.position.set(x, y - 2);
        this.refs.cubes.addChild(label);
      }
    }
  }

  private renderButtons(): void {
    if (!this.state || !this.refs) return;
    this.refs.buttons.removeChildren();
    const values = [...this.state.available_blocks, ...LETTER_COMMANDS];
    values.forEach((value, index) => {
      const command = LETTER_COMMANDS.includes(value);
      const row = Math.floor(index / 6);
      const col = index % 6;
      const x = 70 + col * 84;
      const y = this.app.screen.height - 46 - row * 52;
      const button = new Graphics()
        .roundRect(-34, -19, 68, 38, 13)
        .fill(command ? 0x37515d : 0xffdc7a)
        .stroke({ color: command ? 0xa8d8ef : 0x70451e, width: 2, alpha: 0.7 });
      button.position.set(x, y);
      button.eventMode = "static";
      button.cursor = "pointer";
      button.on("pointertap", (event: FederatedPointerEvent) => {
        event.stopPropagation();
        void this.sendInput(value);
      });
      const label = this.makeText(value, command ? 14 : 20, command ? "#f5fbff" : "#3a2412", 900);
      label.anchor.set(0.5);
      label.position.set(x, y - 1);
      this.refs.buttons.addChild(button, label);
    });
  }

  private async sendInput(value: string): Promise<void> {
    const state = await this.client.sendInput(value);
    this.playEvents(state.events || []);
    this.render(state);
  }

  private playEvents(events: MissionEvent[]): void {
    const completed = events.some((event) => event.type === "mission_completed" || event.type === "scene_restored");
    if (!completed) return;
    const { width, height } = this.app.screen;
    this.refs.celebration.clear()
      .circle(width * 0.73, height * 0.45, 160)
      .fill({ color: 0xffe58b, alpha: 0.42 })
      .circle(width * 0.18, height * 0.47, 84)
      .fill({ color: 0xa8f6bf, alpha: 0.28 });
    this.refs.celebration.alpha = 1;
  }

  private renderDebug(): void {
    if (!this.state || !this.refs) return;
    this.refs.debug.text = [
      `ws ${this.socketStatus}`,
      `mision ${this.state.mission_id}`,
      `bloques ${JSON.stringify(this.state.current_blocks)}`,
      `estado ${this.state.status}`,
      `siguiente ${this.state.expected_next_block ?? "-"}`,
    ].join("\n");
    this.refs.debug.position.set(this.app.screen.width - 238, 22);
  }

  private makeText(value: string, size: number, color: string, weight = 700, family = "Nunito, Segoe UI, Arial"): Text {
    const fontWeight = String(weight) as "100" | "200" | "300" | "400" | "500" | "600" | "700" | "800" | "900";
    return new Text({
      text: value,
      style: {
        fill: color,
        fontFamily: family,
        fontSize: size,
        fontWeight,
        lineHeight: Math.round(size * 1.22),
      },
    });
  }
}
