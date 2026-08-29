import { test, expect } from "@playwright/test";

test.setTimeout(90000);

test("4D timeline changes map hazard and evacuation-flow sources", async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort());
  await page.goto("/admin?demo=1", { waitUntil: "domcontentloaded", timeout: 60000 });
  await expect(page.getByRole("heading", { name: "안양 안전 운영 도구" })).toBeVisible({ timeout: 30000 });
  await expect(page.getByRole("slider", { name: "4D 시뮬레이션 타임라인" })).toBeVisible({ timeout: 30000 });
  const sourceData = (sourceId: string) => page.evaluate((id) => {
    const map = (window as Window & { __SAFE_TWIN_MAP__?: { getSource: (name: string) => { _data?: unknown } | undefined } }).__SAFE_TWIN_MAP__;
    return JSON.stringify(map?.getSource(id)?._data ?? null);
  }, sourceId);
  const hazardAtStart = await sourceData("scenario-hazard");
  const flowAtStart = await sourceData("evacuation-flow");
  const slider = page.getByRole("slider", { name: "4D 시뮬레이션 타임라인" });
  await slider.press("ArrowRight");
  await expect(page.getByText(/10분 frame/)).toBeVisible({ timeout: 30000 });
  await expect.poll(() => sourceData("scenario-hazard")).not.toBe(hazardAtStart);
  await expect.poll(() => sourceData("evacuation-flow")).not.toBe(flowAtStart);
});
