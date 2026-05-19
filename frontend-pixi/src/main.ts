import "./styles.css";
import { SilaPixiGame } from "./pixi/SilaPixiGame";

const root = document.getElementById("app");
if (!root) {
  throw new Error("Missing app root");
}

const loading = document.createElement("div");
loading.className = "loading";
loading.textContent = "Cargando SilaBlocks...";
root.appendChild(loading);

const game = new SilaPixiGame(root);
void game.init().then(() => loading.remove());

