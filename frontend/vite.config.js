import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, forward /api calls to the FastAPI server (default port 8001).
// Override with:  set API_TARGET=http://127.0.0.1:8000  (Windows cmd)
const target = process.env.API_TARGET ?? "http://127.0.0.1:8001";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { "/api": target } },
});
