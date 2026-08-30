import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.beforeEach(async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort());
});

test.setTimeout(120000);

test("admin simulator exposes real data, timeline, training boundary, and axe-clean controls", async ({ page }) => {
  await page.goto("/admin", { waitUntil: "commit", timeout: 60000 });
  await expect(page.getByRole("heading", { name: "안양 안전 운영 도구" })).toBeVisible({ timeout: 30000 });
  await expect(page.getByText("훈련/가정 시나리오", { exact: true })).toBeVisible();
  await expect(page.getByText(/공식 비상급수 맥락/)).toBeVisible({ timeout: 30000 });
  await expect(page.getByRole("button", { name: "훈련 경로 계산" })).toBeVisible();
  await page.screenshot({ path: "artifacts/evals/ui/goal4a-admin-1280x720.png", fullPage: true });
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((item) => ["serious", "critical"].includes(item.impact ?? ""))).toEqual([]);
});

test("admin simulator remains usable on phone viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/admin", { waitUntil: "commit", timeout: 60000 });
  await expect(page.getByRole("heading", { name: "안양 안전 운영 도구" })).toBeVisible({ timeout: 30000 });
  await page.screenshot({ path: "artifacts/evals/ui/goal4a-admin-390x844.png", fullPage: true });
});

test("admin demo keeps AI estimates separate from exact verification", async ({ page }) => {
  await page.route("http://127.0.0.1:8000/api/admin/goal5a/screen", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        candidate_count: 100,
        exact_calls: 1,
        model_version: "goal5a-scenario-triage-v1",
        verified_shortlist: [{
          scenario_id: "goal5a-demo-001",
          estimated_unserved: 1200,
          exact_verified: true,
          exact_result: { unserved: 1180 },
          support_status: "AI_ESTIMATE_SUPPORTED",
          explanation: [{ feature: "evacuation_demand" }],
        }],
      }),
    });
  });
  await page.goto("/admin?demo=1", { waitUntil: "commit", timeout: 60000 });
  await page.getByRole("button", { name: "고급 분석" }).click();
  await expect(page.getByRole("heading", { name: "AI 대규모 시나리오 선별" })).toBeVisible({ timeout: 30000 });
  await page.getByRole("button", { name: "AI 빠른 선별" }).click();
  await expect(page.getByText(/100개 후보 · exact 호출 1회/)).toBeVisible({ timeout: 30000 });
  await expect(page.getByText(/AI 추정 미배정 1,200명 · exact 미배정 1,180명/)).toBeVisible();
  await expect(page.getByText(/표시 최종값은 exact reference 결과/)).toBeVisible();
});

test("admin authoring, timeline, A/B comparison, export, and visual matrix", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/admin", { waitUntil: "commit", timeout: 60000 });
  await expect(page.getByRole("heading", { name: "안양 안전 운영 도구" })).toBeVisible({ timeout: 30000 });
  await expect(page.getByText("감소된 동작")).toBeVisible({ timeout: 30000 });

  const timeline = page.getByRole("slider", { name: "4D 시뮬레이션 타임라인" });
  await timeline.focus();
  await timeline.press("ArrowRight");
  await expect(page.getByText(/10분 frame/)).toBeVisible({ timeout: 30000 });
  await page.getByRole("button", { name: "재생" }).click();
  await page.getByRole("button", { name: "일시정지" }).click();

  const compare = page.getByRole("combobox", { name: "Scenario B 비교 대상" });
  await compare.selectOption({ index: 1 });
  await page.getByRole("button", { name: "차이 계산" }).click();
  await expect(page.getByText(/B−A 배정/)).toBeVisible({ timeout: 30000 });

  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "JSON 내보내기" }).click();
  expect((await download).suggestedFilename()).toMatch(/\.json$/);

  for (const [width, height] of [[768, 1024], [1440, 900]] as const) {
    await page.setViewportSize({ width, height });
    await page.screenshot({ path: `artifacts/evals/ui/goal4a-admin-${width}x${height}-ab.png`, fullPage: true });
  }
});
