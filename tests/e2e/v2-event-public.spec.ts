import { test, expect } from "@playwright/test";

test.setTimeout(60000);

test("public event page exposes share QR and advances deterministic video scenes", async ({ page }) => {
  await page.goto("/event/anyang-demo", { waitUntil: "domcontentloaded", timeout: 30000 });
  await expect(page.getByRole("heading", { name: "SAFE-Twin 행사 대피 안내" })).toBeVisible();
  await expect.poll(async () => (await page.getByAltText("행사 대피 안내 공개 URL QR 코드").count()) > 0 || (await page.getByText(/QR 이미지를 불러오지 못했습니다/).count()) > 0).toBe(true);
  await expect(page.locator(".event-share code")).toContainText("/event/");
  const qr = page.locator(".event-share img");
  await expect(qr).toHaveAttribute("src", /api\.qrserver\.com\/v1\/create-qr-code/);
  const qrTarget = await qr.evaluate((image) => new URL(image.getAttribute("src") || "").searchParams.get("data"));
  expect(qrTarget).toContain("/event/");
  const sharedPage = await page.context().newPage();
  await sharedPage.goto(qrTarget as string, { waitUntil: "domcontentloaded" });
  await expect(sharedPage.getByRole("heading", { name: "SAFE-Twin 행사 대피 안내" })).toBeVisible();
  await sharedPage.close();
  const before = await page.getByTestId("event-video-canvas").getAttribute("data-scene-index");
  await page.getByRole("button", { name: "재생" }).click();
  await page.waitForTimeout(3500);
  const after = await page.getByTestId("event-video-canvas").getAttribute("data-scene-index");
  expect(after).not.toBe(before);
  await page.getByRole("button", { name: "일시정지" }).click();
  const downloadPromise = page.waitForEvent("download", { timeout: 10000 });
  await page.getByRole("button", { name: "WebM 내보내기" }).click();
  const download = await downloadPromise;
  const downloadPath = await download.path();
  expect(downloadPath).toBeTruthy();
  const videoBytes = await (await import("node:fs/promises")).readFile(downloadPath as string);
  expect(videoBytes.byteLength).toBeGreaterThan(0);
  expect(videoBytes.subarray(0, 4).toString("hex")).toBe("1a45dfa3");
  await page.screenshot({ path: "artifacts/evals/v2/screenshots/event-public-video-1280.png", fullPage: true });
});

test("organizer draws an image-local indoor evacuation route", async ({ page }, testInfo) => {
  await page.goto("/event-admin", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "행사 대피안내 만들기" })).toBeVisible();
  await page.getByLabel("행사명").fill("실내 안전 교육");
  await page.getByLabel("행사 장소").fill("안양 강당");
  await page.getByRole("button", { name: "다음" }).click();
  await page.getByLabel("실내 도면").check();
  await page.getByRole("button", { name: "다음" }).click();
  const surface = page.getByTestId("floor-plan-surface");
  await expect(surface).toBeVisible();
  await surface.click({ position: { x: 120, y: 90 } });
  await page.getByLabel("안내 지점 종류").selectOption("exit");
  await surface.click({ position: { x: 600, y: 100 } });
  await page.getByLabel("안내 지점 종류").selectOption("assembly");
  await surface.click({ position: { x: 700, y: 400 } });
  await page.getByRole("button", { name: "경로 그리기" }).click();
  await surface.click({ position: { x: 240, y: 90 } });
  await surface.click({ position: { x: 420, y: 95 } });
  await page.getByRole("button", { name: "경로 그리기 종료" }).click();
  await expect(surface.locator("polyline")).toBeVisible();
  await expect(page.getByText(/도면 좌표 800×500/)).toBeVisible();
  for (const [width, height] of [[390, 844], [768, 1024], [1280, 720], [1440, 900]] as const) {
    await page.setViewportSize({ width, height });
    await page.screenshot({ path: `artifacts/evals/v2/screenshots/event-organizer-indoor-${width}x${height}-${testInfo.project.name}.png`, fullPage: true });
  }
});

test("organizer publishes an outdoor map route with safety points", async ({ page }) => {
  await page.goto("/event-admin", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "행사 대피안내 만들기" })).toBeVisible();
  await page.getByLabel("행사명").fill("야외 캠퍼스 행사");
  await page.getByLabel("행사 장소").fill("안양 캠퍼스");
  await page.getByRole("button", { name: "다음" }).click();
  await page.getByRole("button", { name: "다음" }).click();
  const map = page.locator(".event-outdoor-editor .real-map");
  await expect(map.locator(".maplibregl-canvas")).toBeVisible({ timeout: 30000 });
  await map.click({ position: { x: 220, y: 150 } });
  await page.getByLabel("안내 지점 종류").selectOption("exit");
  await map.click({ position: { x: 520, y: 170 } });
  await page.getByLabel("안내 지점 종류").selectOption("assembly");
  await map.click({ position: { x: 600, y: 300 } });
  await page.getByLabel("안내 지점 종류").selectOption("AED");
  await map.click({ position: { x: 420, y: 250 } });
  await page.getByRole("button", { name: "경로 그리기" }).click();
  await map.click({ position: { x: 300, y: 160 } });
  await map.click({ position: { x: 420, y: 180 } });
  await expect.poll(async () => page.evaluate(() => {
    const map = (window as Window & { __SAFE_TWIN_MAP__?: { getSource: (id: string) => { serialize?: () => { data?: { features?: Array<{ geometry?: { type?: string; coordinates?: unknown[] } }> } } } | undefined } }).__SAFE_TWIN_MAP__;
    const data = map?.getSource("walking-route")?.serialize?.().data;
    const line = data?.features?.find((feature) => feature.geometry?.type === "LineString");
    return line?.geometry?.coordinates?.length ?? 0;
  })).toBeGreaterThanOrEqual(5);
  await page.getByRole("button", { name: "계획 미리보기" }).last().click();
  await expect(page.getByRole("heading", { name: "야외 캠퍼스 행사" })).toBeVisible();
  await expect(page.getByText("AED").last()).toBeVisible();
  await expect(page.getByText("지정됨").first()).toBeVisible();
  await expect(page.getByTestId("walking-route-line")).toBeVisible();
});
