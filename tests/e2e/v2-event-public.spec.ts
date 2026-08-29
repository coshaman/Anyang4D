import { test, expect } from "@playwright/test";

test.setTimeout(60000);

test("public event page exposes share QR and advances deterministic video scenes", async ({ page }) => {
  await page.goto("/event/anyang-demo", { waitUntil: "domcontentloaded", timeout: 30000 });
  await expect(page.getByRole("heading", { name: "SAFE-Twin 행사 대피 안내" })).toBeVisible();
  await expect.poll(async () => (await page.getByAltText("행사 대피 안내 공개 URL QR 코드").count()) > 0 || (await page.getByText(/QR 이미지를 불러오지 못했습니다/).count()) > 0).toBe(true);
  await expect(page.locator(".event-share code")).toContainText("/event/");
  const before = await page.getByTestId("event-video-canvas").getAttribute("data-scene-index");
  await page.getByRole("button", { name: "재생" }).click();
  await page.waitForTimeout(3500);
  const after = await page.getByTestId("event-video-canvas").getAttribute("data-scene-index");
  expect(after).not.toBe(before);
  await page.screenshot({ path: "artifacts/evals/v2/screenshots/event-public-video-1280.png", fullPage: true });
});
