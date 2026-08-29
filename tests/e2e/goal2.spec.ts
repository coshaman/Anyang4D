import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import type { Page } from "@playwright/test";

async function seriousAxe(page: Page) {
  const results = await new AxeBuilder({ page }).analyze();
  return results.violations.filter((violation) => ["serious", "critical"].includes(violation.impact ?? ""));
}

test.beforeEach(async ({ page }) => {
  // The app keeps the real OSM tile source; CI/browser sandboxes may not have outbound tile access.
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort());
});

test("citizen normal state is real-data and map-first", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "안양 재난 대응 지도" })).toBeVisible();
  await expect(page.getByText("공식 데이터 기준")).toBeVisible();
  await expect(page.getByRole("group", { name: "시설 종류" }).getByRole("button", { name: "대피소" })).toContainText("231");
  await expect(page.getByLabel("안양 실제 지도")).toBeVisible();
  expect(await seriousAxe(page)).toEqual([]);
});

test("AED flow keeps 119 first and preserves missing coordinates", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "AED" }).click();
  await page.getByRole("button", { name: "AED 찾기" }).click();
  await expect(page.getByRole("link", { name: /119 신고/ }).first()).toHaveAttribute("href", "tel:119");
  await expect(page.getByText(/AED 원문에는 좌표가 없습니다/)).toBeVisible();
  expect(await seriousAxe(page)).toEqual([]);
});

test("coordinate-bearing facility draws the basic walking route line", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "대피소" }).click();
  await page.locator(".nearby-list > button").first().click();
  await page.getByRole("button", { name: "기본 도보 경로 보기" }).click();
  await expect(page.getByTestId("walking-route-line")).toBeVisible({ timeout: 30000 });
  await expect(page.getByText(/기본 도보 경로.*예상.*출처/)).toBeVisible();
});

test("large text, geolocation denial, offline state, and preview shell are honest", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.getByRole("button", { name: "큰 글씨" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "large");
  await page.evaluate(() => {
    navigator.geolocation.getCurrentPosition = (_success, error) => error?.({ code: 1, message: "denied" } as GeolocationPositionError);
  });
  await page.getByRole("button", { name: "현재 위치" }).click();
  await expect(page.getByText(/위치를 허용하지 않아/)).toBeVisible();
  await page.context().setOffline(true);
  await page.evaluate(() => window.dispatchEvent(new Event("offline")));
  await expect(page.getByText(/오프라인 · 저장된 정보/)).toBeVisible();
  await page.context().setOffline(false);
  await page.getByRole("button", { name: "재난 상황 미리보기" }).click();
  await expect(page.getByRole("heading", { name: "재난 상황 미리보기" })).toBeVisible();
  await expect(page.getByText("훈련/가정 시나리오")).toBeVisible();
  await expect(page.getByText("대피 수요")).toBeVisible({ timeout: 30000 });
  await page.screenshot({ path: `artifacts/evals/ui/goal2-training-preview-${testInfo.project.name}.png`, fullPage: true });
  expect(await seriousAxe(page)).toEqual([]);
});

test("required viewport visual matrix and 200 percent zoom", async ({ page }, testInfo) => {
  const viewports = [[320, 568], [360, 800], [390, 844], [430, 932], [768, 1024], [1024, 768], [1280, 720], [1440, 900]] as const;
  for (const [width, height] of viewports) {
    await page.setViewportSize({ width, height });
    await page.goto("/");
    await page.screenshot({ path: `artifacts/evals/ui/goal2-${width}x${height}.png`, fullPage: true });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.evaluate(() => { document.documentElement.style.zoom = "2"; });
  await page.screenshot({ path: `artifacts/evals/ui/goal2-200-percent-${testInfo.project.name}.png`, fullPage: true });
});
