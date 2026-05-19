import { defineConfig } from "vite";

const backend = "http://localhost:5000";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 5174,
    proxy: {
      "/health": backend,
      "/buffer": backend,
      "/progress": backend,
      "/shop": backend,
      "/buy": backend,
      "/nfc": backend,
      "/mission": backend,
      "/decorations": backend,
      "/ws": {
        target: "ws://localhost:5000",
        ws: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 4174,
  },
});

