/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ["maplibre-gl"]
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./apps/web/src/test-setup.ts"],
    css: true,
    include: ["apps/web/src/**/*.test.{ts,tsx}"]
  }
});
