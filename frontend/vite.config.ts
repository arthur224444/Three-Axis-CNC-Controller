import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiProxy = {
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
};

export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: "../pi5/static",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/health": apiProxy,
      "/commands": apiProxy,
      "/axis": apiProxy,
      "/spindle": apiProxy,
      "/emergency-stop": apiProxy,
      "/noop": apiProxy,
      "/docs": apiProxy,
      "/redoc": apiProxy,
      "/openapi.json": apiProxy,
    },
  },
});
