import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

test.describe.configure({ mode: "serial" });
test.setTimeout(180000);

const root = process.cwd();
const screenshotDir = path.join(root, "artifacts", "competition", "screenshots");
const timingPath = path.join(root, "artifacts", "evals", "performance", "goal6a-demo-runtime.json");

test("capture real competition demo screens and presenter timings", async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort());
  fs.mkdirSync(screenshotDir, { recursive: true });
  const timings: Record<string, number | string> = {};
  const measure = async (name: string, action: () => Promise<void>) => {
    const started = Date.now();
    await action();
    timings[name] = Date.now() - started;
  };

  await measure("demo_route_to_usable_admin", async () => {
    await page.goto("/admin?demo=1", { waitUntil: "commit", timeout: 60000 });
    await expect(page.getByRole("heading", { name: "안양 안전 운영 도구" })).toBeVisible({ timeout: 60000 });
    await expect(page.locator(".maplibregl-canvas")).toBeVisible({ timeout: 60000 });
  });
  await page.screenshot({ path: path.join(screenshotDir, "03-admin-demo-opening.png"), fullPage: true });

  await measure("timeline_mid_state", async () => {
    const slider = page.getByRole("slider", { name: "4D 시뮬레이션 타임라인" });
    await slider.focus();
    await slider.press("ArrowRight");
    await expect(page.getByText(/10분 frame/)).toBeVisible({ timeout: 60000 });
  });
  await page.screenshot({ path: path.join(screenshotDir, "04-admin-timeline-mid-state.png"), fullPage: true });

  await measure("ab_compare", async () => {
    const compare = page.getByRole("combobox", { name: "Scenario B 비교 대상" });
    await compare.selectOption({ index: 1 });
    await page.getByRole("button", { name: "차이 계산" }).click();
    await expect(page.getByText(/B−A 배정/)).toBeVisible({ timeout: 60000 });
  });
  await page.screenshot({ path: path.join(screenshotDir, "05-scenario-ab.png"), fullPage: true });

  await measure("ai_screen_and_exact_verification", async () => {
    await page.getByRole("button", { name: "고급 분석" }).click();
    await page.getByRole("button", { name: "AI 빠른 선별" }).click();
    await expect(page.getByText(/AI 선별 완료/)).toBeVisible({ timeout: 120000 });
  await expect(page.getByText(/표시 최종값은 exact reference 결과/)).toBeVisible({ timeout: 120000 });
  });
  await page.screenshot({ path: path.join(screenshotDir, "06-ai-screening-and-exact-verification.png"), fullPage: true });

  await measure("export", async () => {
    await page.getByRole("button", { name: "재난 시뮬레이션" }).click();
    const download = page.waitForEvent("download");
    await page.getByRole("button", { name: "JSON 내보내기" }).click();
    await download;
  });

  await page.goto("/", { waitUntil: "commit", timeout: 60000 });
  await expect(page.getByRole("heading", { name: "안양 재난 대응 지도" })).toBeVisible({ timeout: 60000 });
  await page.screenshot({ path: path.join(screenshotDir, "01-citizen-map.png"), fullPage: true });
  await page.getByRole("button", { name: "큰 글씨" }).click();
  await page.screenshot({ path: path.join(screenshotDir, "09-citizen-large-text.png"), fullPage: true });
  await page.getByRole("button", { name: "데이터 출처와 한계" }).click();
  await expect(page.getByRole("heading", { name: "데이터 출처와 한계" })).toBeVisible({ timeout: 60000 });
  await page.screenshot({ path: path.join(screenshotDir, "08-provenance-panel.png"), fullPage: true });

  timings["network_tile_failure_behavior"] = "layout and vector/data panels remain visible with tile requests aborted";
  timings["screenshots"] = 7;
  timings["measurement_mode"] = "real browser, real backend, no mocked core requests";
  fs.mkdirSync(path.dirname(timingPath), { recursive: true });
  fs.writeFileSync(timingPath, JSON.stringify({ schema_version: "goal6a-demo-runtime-v1", status: "PASS", timings, api: { base: "http://127.0.0.1:8000", ai_candidate_count: 100, exact_verification_required: true }, caveats: ["Timings are one local Windows CPU run; they are not a hosted SLA.", "OSM tile requests were aborted to verify safe offline layout behavior; official/local data and vector overlays remained available."] }, null, 2) + "\n");
});
