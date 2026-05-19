import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/health": "http://localhost:5000",
      "/buffer": "http://localhost:5000",
      "/progress": "http://localhost:5000",
      "/shop": "http://localhost:5000",
      "/buy": "http://localhost:5000",
      "/nfc": "http://localhost:5000",
      "/mission": "http://localhost:5000",
      "/decorations": "http://localhost:5000",
      "/ws": {
        target: "ws://localhost:5000",
        ws: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
  },
});
