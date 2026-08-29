import { test, expect } from "@playwright/test";

test.setTimeout(60000);

test("citizen map exposes a real 3D building layer and camera controls", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded", timeout: 30000 });
  await expect(page.getByTestId("map-3d-toggle")).toBeVisible();
  await page.getByTestId("map-3d-toggle").click();
  await expect(page.getByText("3D 건물 높이")).toBeVisible();
  await page.screenshot({ path: "artifacts/evals/v2/screenshots/citizen-3d-1280.png", fullPage: true });
  await expect.poll(async () => page.evaluate(() => {
    const map = (window as Window & { __SAFE_TWIN_MAP__?: { getSource: (id: string) => unknown; getLayer: (id: string) => { type?: string } | undefined; getPitch: () => number } }).__SAFE_TWIN_MAP__;
    return Boolean(map?.getSource("buildings") && map.getLayer("building-extrusion")?.type === "fill-extrusion" && (map.getPitch() ?? 0) > 0);
  })).toBe(true);
  await page.getByRole("button", { name: "북쪽" }).click();
  await expect(page.getByTestId("map-3d-toggle")).toHaveAttribute("aria-pressed", "true");
});
