import { test, expect } from "@playwright/test";

test.setTimeout(180000);
test.beforeEach(async ({ page }) => {
  await page.route("https://tile.openstreetmap.org/**", (route) => route.abort());
});

test("production container exposes real citizen and walking route flows", async ({ page, request }) => {
  expect((await request.get("/readyz")).status()).toBe(200);
  const aed = await request.get("/api/facilities?type=aed");
  expect(aed.status()).toBe(200);
  expect((await aed.json()).items).toHaveLength(305);
  await page.goto("/");
  await expect(page.getByText("대피소 231곳")).toBeVisible();
  await page.getByRole("button", { name: "대피소" }).click();
  await page.locator(".nearby-list button").first().click();
  await page.getByRole("button", { name: "기본 도보 경로 보기" }).click();
  await expect(page.getByTestId("walking-route-line")).toBeVisible({ timeout: 30000 });
  await page.getByRole("button", { name: "AED" }).click();
  await expect(page.getByText("원문에 좌표가 없어 AED는 주소 목록으로 제공합니다.")).toBeVisible();
  await expect(page.getByText("원문 좌표 없음").first()).toBeVisible();
});

test("production container loads citizen training and admin exact flows", async ({ page }) => {
  await page.goto("/simulate");
  await expect(page.getByRole("heading", { name: "재난 상황 미리보기" })).toBeVisible({ timeout: 30000 });
  await expect(page.locator("select").first()).toHaveValue("anyang-general-evacuation-competition", { timeout: 30000 });
  await expect(page.getByText("대피 수요")).toBeVisible({ timeout: 60000 });
  await page.goto("/admin?demo=1");
  await expect(page.getByRole("heading", { name: "안양 4D 도시상태 시뮬레이터" })).toBeVisible();
  await expect(page.getByText(/공식 비상급수 맥락/)).toBeVisible({ timeout: 60000 });
  await expect(page.getByText(/배포 진단/)).toBeVisible();
  await page.getByRole("button", { name: "AI 빠른 선별" }).click();
  await expect(page.getByText(/exact 호출/)).toBeVisible({ timeout: 120000 });
});
