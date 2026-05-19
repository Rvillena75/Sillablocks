import Phaser from "phaser";
import type { MissionState } from "../api/types";
import { storybookAssets } from "./assets";
import { SceneEvents, getLatestMissionState, sceneBus } from "./sceneBus";

interface CubeVisual {
  root: Phaser.GameObjects.Container;
  letter: string;
}

export class StorybookScene extends Phaser.Scene {
  private state: MissionState | null = null;
  private trees: Phaser.GameObjects.Image[] = [];
  private fog: Phaser.GameObjects.Ellipse[] = [];
  private particles: Phaser.GameObjects.Arc[] = [];
  private cubes: CubeVisual[] = [];
  private backdrop!: Phaser.GameObjects.Graphics;
  private hills!: Phaser.GameObjects.Graphics;
  private cubeLayer!: Phaser.GameObjects.Container;
  private lumo!: Phaser.GameObjects.Image;
  private lanternOff!: Phaser.GameObjects.Image;
  private lanternOn!: Phaser.GameObjects.Image;
  private glow!: Phaser.GameObjects.Arc;
  private path!: Phaser.GameObjects.Graphics;
  private previousStatus = "idle";

  constructor() {
    super("StorybookScene");
  }

  preload(): void {
    this.load.svg("tree-soft", storybookAssets.tree, { width: 220, height: 260 });
    this.load.svg("lumo-soft", storybookAssets.lumo, { width: 180, height: 180 });
    this.load.svg("lantern-off", storybookAssets.lanternOff, { width: 160, height: 230 });
    this.load.svg("lantern-on", storybookAssets.lanternOn, { width: 220, height: 260 });
    this.load.svg("cube-soft", storybookAssets.cube, { width: 120, height: 120 });
  }

  create(): void {
    this.ensureFallbackTextures();
    this.createWorld();
    sceneBus.on(SceneEvents.stateChanged, this.renderState, this);
    const latest = getLatestMissionState();
    if (latest) {
      this.renderState(latest);
    }
    this.scale.on("resize", this.layout, this);
  }

  shutdown(): void {
    sceneBus.off(SceneEvents.stateChanged, this.renderState, this);
    this.scale.off("resize", this.layout, this);
  }

  private createWorld(): void {
    this.backdrop = this.add.graphics();
    this.hills = this.add.graphics();
    this.path = this.add.graphics();

    for (let i = 0; i < 9; i += 1) {
      const tree = this.add.image(0, 0, "tree-soft");
      tree.setOrigin(0.5, 1);
      tree.setAlpha(i < 3 ? 0.75 : 1);
      this.trees.push(tree);
    }

    this.glow = this.add.circle(0, 0, 112, 0xf4c84a, 0.12);
    this.lanternOff = this.add.image(0, 0, "lantern-off").setOrigin(0.5, 0.9);
    this.lanternOn = this.add.image(0, 0, "lantern-on").setOrigin(0.5, 0.9).setAlpha(0);
    this.lumo = this.add.image(0, 0, "lumo-soft").setScale(0.72);
    this.cubeLayer = this.add.container(0, 0);

    for (let i = 0; i < 5; i += 1) {
      const puff = this.add.ellipse(0, 0, 240, 46, 0xfff8e7, 0.18);
      this.fog.push(puff);
    }

    for (let i = 0; i < 26; i += 1) {
      const particle = this.add.circle(0, 0, 2 + (i % 3), 0xf4c84a, 0.3);
      this.particles.push(particle);
    }

    this.tweens.add({
      targets: this.lumo,
      y: "+=18",
      duration: 1800,
      yoyo: true,
      repeat: -1,
      ease: "Sine.inOut",
    });
    this.tweens.add({
      targets: this.glow,
      alpha: 0.22,
      scale: 1.08,
      duration: 1600,
      yoyo: true,
      repeat: -1,
      ease: "Sine.inOut",
    });
    this.layout();
  }

  private layout(): void {
    const { width, height } = this.scale;
    this.drawBackdrop();
    this.drawPath();

    const positions = [
      [0.08, 0.56, 0.88],
      [0.20, 0.50, 0.74],
      [0.34, 0.55, 0.92],
      [0.64, 0.53, 0.86],
      [0.78, 0.48, 0.78],
      [0.92, 0.56, 0.95],
      [0.12, 0.82, 1.22],
      [0.88, 0.83, 1.18],
      [0.50, 0.66, 0.78],
    ];
    this.trees.forEach((tree, index) => {
      const [x, y, scale] = positions[index];
      tree.setPosition(width * x, height * y);
      tree.setScale(scale);
    });

    this.glow.setPosition(width * 0.72, height * 0.48);
    this.lanternOff.setPosition(width * 0.72, height * 0.66);
    this.lanternOn.setPosition(width * 0.72, height * 0.66);
    this.lumo.setPosition(width * 0.24, height * 0.48);
    this.fog.forEach((puff, index) => {
      puff.setPosition(width * (0.24 + index * 0.16), height * (0.66 + (index % 2) * 0.04));
    });
    this.renderCubes();
  }

  private drawBackdrop(): void {
    const { width, height } = this.scale;
    this.backdrop.clear();
    this.backdrop.fillStyle(0x14382f, 1);
    this.backdrop.fillRect(0, 0, width, height);
    this.backdrop.fillStyle(0x62c7e8, 0.13);
    this.backdrop.fillEllipse(width * 0.24, height * 0.22, width * 0.55, height * 0.28);
    this.backdrop.fillStyle(0xf4c84a, 0.10);
    this.backdrop.fillEllipse(width * 0.75, height * 0.28, width * 0.48, height * 0.30);

    this.hills.clear();
    this.hills.fillStyle(0x2f7149, 1);
    this.hills.fillEllipse(width * 0.28, height * 0.82, width * 0.72, height * 0.48);
    this.hills.fillEllipse(width * 0.78, height * 0.80, width * 0.82, height * 0.52);
    this.hills.fillStyle(0x3f8f5a, 1);
    this.hills.fillEllipse(width * 0.50, height * 0.98, width * 1.34, height * 0.52);
  }

  private drawPath(): void {
    const { width, height } = this.scale;
    this.path.clear();
    this.path.fillStyle(0x7a4e2a, 0.28);
    this.path.fillPoints([
      new Phaser.Math.Vector2(width * 0.42, height * 0.58),
      new Phaser.Math.Vector2(width * 0.37, height * 0.70),
      new Phaser.Math.Vector2(width * 0.32, height * 0.88),
      new Phaser.Math.Vector2(width * 0.18, height),
      new Phaser.Math.Vector2(width * 0.82, height),
      new Phaser.Math.Vector2(width * 0.65, height * 0.88),
      new Phaser.Math.Vector2(width * 0.60, height * 0.70),
      new Phaser.Math.Vector2(width * 0.55, height * 0.58),
    ], true);
  }

  private renderState(state: MissionState): void {
    this.state = state;
    const success = state.status === "success" || state.status === "demo_complete";
    this.tweens.add({
      targets: this.lanternOn,
      alpha: success ? 1 : 0,
      duration: 420,
      ease: "Sine.out",
    });
    this.tweens.add({
      targets: this.lanternOff,
      alpha: success ? 0 : 1,
      duration: 420,
      ease: "Sine.out",
    });
    this.tweens.add({
      targets: this.fog,
      alpha: success ? 0.03 : Math.max(0.10, 0.24 - state.progress_percent / 500),
      duration: 700,
      ease: "Sine.out",
    });

    if (state.status === "success" && this.previousStatus !== "success") {
      this.celebrate();
    }
    this.previousStatus = state.status;
    this.renderCubes();
  }

  private renderCubes(): void {
    if (!this.state || !this.cubeLayer) return;
    const { width, height } = this.scale;
    const existing = this.cubes.map((cube) => cube.letter).join("");
    const next = this.state.current_blocks.join("");
    this.cubeLayer.removeAll(true);
    this.cubes = [];
    const total = Math.max(this.state.target_blocks.length, 1);
    const startX = width * 0.5 - ((total - 1) * 78) / 2;
    for (let i = 0; i < total; i += 1) {
      const letter = this.state.current_blocks[i] ?? "";
      const root = this.add.container(startX + i * 78, height * 0.78);
      const shadow = this.add.ellipse(0, 38, 58, 13, 0x1d2b24, 0.18);
      const cube = this.add.image(0, 0, "cube-soft").setScale(0.58).setAlpha(letter ? 1 : 0.34);
      root.add([shadow, cube]);
      if (letter) {
        const label = this.add.text(0, -2, letter, {
          color: "#1D2B24",
          fontFamily: "Fredoka, Nunito, Arial",
          fontSize: "32px",
          fontStyle: "bold",
        }).setOrigin(0.5);
        root.add(label);
      }
      if (letter && next.length > existing.length && i === this.state.current_blocks.length - 1) {
        root.setScale(0.25);
        root.setAlpha(0);
        this.tweens.add({ targets: root, scale: 1, alpha: 1, duration: 360, ease: "Back.out" });
      }
      this.cubeLayer.add(root);
      this.cubes.push({ root, letter });
    }
  }

  private celebrate(): void {
    const { width, height } = this.scale;
    this.particles.forEach((particle, index) => {
      const angle = (Math.PI * 2 * index) / this.particles.length;
      particle.setPosition(width * 0.72, height * 0.48);
      particle.setAlpha(0.9);
      this.tweens.add({
        targets: particle,
        x: width * 0.72 + Math.cos(angle) * (80 + (index % 4) * 26),
        y: height * 0.48 + Math.sin(angle) * (60 + (index % 5) * 20),
        alpha: 0,
        duration: 900,
        ease: "Sine.out",
      });
    });
  }

  private ensureFallbackTextures(): void {
    this.createTreeTexture();
    this.createLumoTexture();
    this.createLanternTexture("lantern-off", false);
    this.createLanternTexture("lantern-on", true);
    this.createCubeTexture();
  }

  private createTreeTexture(): void {
    if (this.textures.exists("tree-soft")) return;
    const texture = this.make.graphics({ x: 0, y: 0 }, false);
    texture.fillStyle(0x7a4e2a, 1).fillRoundedRect(92, 118, 36, 126, 16);
    texture.fillStyle(0x3f8f5a, 1).fillCircle(74, 92, 48);
    texture.fillStyle(0x4da96b, 1).fillCircle(126, 70, 58);
    texture.fillStyle(0x7bc878, 1).fillCircle(94, 133, 50);
    texture.fillStyle(0x59b96d, 0.68).fillCircle(132, 128, 56);
    texture.generateTexture("tree-soft", 220, 260);
    texture.destroy();
  }

  private createLumoTexture(): void {
    if (this.textures.exists("lumo-soft")) return;
    const texture = this.make.graphics({ x: 0, y: 0 }, false);
    texture.fillStyle(0xf4c84a, 0.24).fillCircle(90, 92, 67);
    texture.fillStyle(0xfff3d1, 1).fillCircle(90, 92, 58);
    texture.fillStyle(0x1d2b24, 1).fillCircle(68, 85, 7).fillCircle(111, 85, 7);
    texture.lineStyle(8, 0xe85d4f, 1).beginPath().arc(91, 105, 22, 0.2, Math.PI - 0.2).strokePath();
    texture.fillStyle(0x62c7e8, 1).fillCircle(29, 50, 14);
    texture.generateTexture("lumo-soft", 180, 180);
    texture.destroy();
  }

  private createLanternTexture(key: string, lit: boolean): void {
    if (this.textures.exists(key)) return;
    const texture = this.make.graphics({ x: 0, y: 0 }, false);
    if (lit) {
      texture.fillStyle(0xf4c84a, 0.28).fillCircle(110, 96, 82);
    }
    texture.fillStyle(0x7a4e2a, 1).fillRoundedRect(104, 132, 14, 100, 7);
    texture.fillStyle(0x7a4e2a, 1).fillRoundedRect(72, 64, 76, 108, 18);
    texture.fillStyle(lit ? 0xfff3d1 : 0x3a2f25, 1).fillRoundedRect(86, 86, 48, 58, 12);
    if (lit) {
      texture.fillStyle(0xf4c84a, 1).fillCircle(110, 115, 22);
    }
    texture.generateTexture(key, 220, 260);
    texture.destroy();
  }

  private createCubeTexture(): void {
    if (this.textures.exists("cube-soft")) return;
    const texture = this.make.graphics({ x: 0, y: 0 }, false);
    texture.fillStyle(0x1d2b24, 0.18).fillEllipse(60, 102, 76, 20);
    texture.fillStyle(0xfff3d1, 1).fillRoundedRect(20, 16, 80, 80, 22);
    texture.fillStyle(0xf4c84a, 0.22).fillRoundedRect(20, 16, 80, 80, 22);
    texture.lineStyle(6, 0x7a4e2a, 1).strokeRoundedRect(20, 16, 80, 80, 22);
    texture.generateTexture("cube-soft", 120, 120);
    texture.destroy();
  }
}
