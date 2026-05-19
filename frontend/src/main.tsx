import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { App } from "./App";

const root = document.getElementById("game");
if (!root) {
  throw new Error("Missing #game root");
}

createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

