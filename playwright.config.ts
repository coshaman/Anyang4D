import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  webServer: [
    { command: "..\\.venv\\Scripts\\python.exe -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000", port: 8000, reuseExistingServer: true },
    { command: "npx vite --host 127.0.0.1 --port 5173", port: 5173, reuseExistingServer: true },
  ],
  use: { baseURL: "http://127.0.0.1:5173", trace: "retain-on-failure" },
  projects: [
    { name: "phone", use: { ...devices["Desktop Chrome"], viewport: { width: 390, height: 844 }, isMobile: true } },
    { name: "desktop", use: { ...devices["Desktop Chrome"] } }
  ]
});
