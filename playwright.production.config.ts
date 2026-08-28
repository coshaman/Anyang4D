import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "production-recovery.spec.ts",
  use: { baseURL: process.env.SAFE_TWIN_PRODUCTION_URL ?? "http://127.0.0.1:8090", ...devices["Desktop Chrome"] },
  workers: 1,
});
