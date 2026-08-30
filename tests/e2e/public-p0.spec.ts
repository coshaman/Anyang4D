import { test, expect } from "@playwright/test";

test.setTimeout(180000);
const publicBase = process.env.PUBLIC_BASE_URL ?? "https://anyang4d.onrender.com";
test.skip(!process.env.PUBLIC_BASE_URL, "외부 공개 배포 검증은 PUBLIC_BASE_URL을 지정한 경우에만 실행합니다.");

async function wake(page: import("@playwright/test").Page) {
  await page.goto(`${publicBase}/healthz`, { waitUntil: "domcontentloaded" });
  await expect(page).toHaveURL(/healthz/);
  await page.goto(`${publicBase}/readyz`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await expect(page).toHaveURL(/readyz/);
}

test("public P0 route renders a nonempty walking-route source", async ({ page }) => {
  await wake(page);
  await page.goto(publicBase);
  await page.getByRole("button", { name: "대피소" }).click();
  await page.locator(".nearby-list button").first().click();
  await page.getByRole("button", { name: "기본 도보 경로 보기" }).click();
  await expect(page.getByTestId("walking-route-line")).toBeVisible({ timeout: 60000 });
  await expect.poll(async () => page.evaluate(() => {
    const map = (window as Window & { __SAFE_TWIN_MAP__?: { getSource: (id: string) => { _data?: { features?: Array<{ geometry?: { type?: string; coordinates?: unknown[] } }> } } | undefined } }).__SAFE_TWIN_MAP__;
    const source = map?.getSource("walking-route") as { serialize?: () => { data?: { features?: Array<{ geometry?: { type?: string; coordinates?: unknown[] } }> } }; _data?: { features?: Array<{ geometry?: { type?: string; coordinates?: unknown[] } }> } } | undefined;
    const data = source?.serialize?.().data ?? source?._data;
    const feature = data?.features?.[0];
    return feature?.geometry?.type === "LineString" && (feature.geometry.coordinates?.length ?? 0) >= 2;
  })).toBe(true);
});

test("public P0 citizen simulation changes computed frame state", async ({ page }) => {
  await wake(page);
  await page.goto(`${publicBase}/simulate`);
  await expect(page.getByRole("heading", { name: "재난 상황 미리보기" })).toBeVisible({ timeout: 60000 });
  await expect(page.getByText("대피 수요")).toBeVisible({ timeout: 60000 });
  const scenario = await (await page.request.get(`${publicBase}/api/admin/goal4a/scenarios`)).json();
  const selected = scenario.items.find((item: { scenario_id: string }) => item.scenario_id === "anyang-civil-defense-outage") ?? scenario.items[0];
  const first = await (await page.request.get(`${publicBase}/api/admin/goal4a/scenarios/${selected.scenario_id}/frames/${selected.frame_times[0]}`)).json();
  const next = await (await page.request.get(`${publicBase}/api/admin/goal4a/scenarios/${selected.scenario_id}/frames/${selected.frame_times[1]}`)).json();
  expect(JSON.stringify(next)).not.toBe(JSON.stringify(first));
  await page.getByRole("button", { name: "재생" }).click();
  await expect(page.getByText(/시간 10분|시간 20분/)).toBeVisible({ timeout: 10000 });
  await expect(page.locator(".training-results")).toContainText(`${next.available_shelter_count}곳`, { timeout: 10000 });
});

test("public P0 admin demo reaches READY and playback changes metrics", async ({ page }) => {
  await wake(page);
  await page.goto(`${publicBase}/admin?demo=1`);
  await expect(page.getByRole("heading", { name: "안양 4D 도시상태 시뮬레이터" })).toBeVisible({ timeout: 60000 });
  await expect(page.getByText(/대회 데모 모드/)).toBeVisible({ timeout: 60000 });
  await expect(page.getByText(/READY/).first()).toBeVisible({ timeout: 60000 });
  await expect(page.getByRole("button", { name: "재생" })).toBeVisible({ timeout: 60000 });
  const before = await page.locator('[aria-label="현재 frame metrics"]').innerText();
  await page.getByRole("button", { name: "재생" }).click();
  await expect.poll(async () => page.locator('[aria-label="현재 frame metrics"]').innerText()).not.toBe(before);
});

test("public P0 A/B comparison displays exact deltas", async ({ page }) => {
  await wake(page);
  await page.goto(`${publicBase}/admin?demo=1`);
  await expect(page.getByRole("button", { name: "차이 계산" })).toBeVisible({ timeout: 60000 });
  await page.getByRole("button", { name: "차이 계산" }).click();
  const delta = page.getByText(/B−A 배정/);
  await expect(delta).toBeVisible({ timeout: 60000 });
  await expect(delta).toContainText("미배정");
  await expect(delta).toContainText("여행 비용");
});
