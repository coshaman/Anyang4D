import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FloorPlanCanvas } from "./FloorPlanCanvas";

describe("floor plan canvas", () => {
  it("supports panning without changing the image-local editing surface", () => {
    render(<FloorPlanCanvas width={800} height={500} onPointAdd={vi.fn()} points={[]} route={[]} />);
    const surface = screen.getByTestId("floor-plan-surface");
    fireEvent.pointerDown(surface, { clientX: 100, clientY: 100, pointerId: 1 });
    fireEvent.pointerMove(surface, { clientX: 140, clientY: 130, pointerId: 1 });
    fireEvent.pointerUp(surface, { clientX: 140, clientY: 130, pointerId: 1 });
    expect(surface.getAttribute("style")).toContain("translate");
  });

  it("converts clicks back to image-local coordinates after zoom and pan", async () => {
    const onPointAdd = vi.fn();
    render(<FloorPlanCanvas width={800} height={500} onPointAdd={onPointAdd} points={[]} route={[]} />);
    const surface = screen.getByTestId("floor-plan-surface");
    vi.spyOn(surface, "getBoundingClientRect").mockReturnValue({ left: 0, top: 0, width: 800, height: 500, right: 800, bottom: 500, x: 0, y: 0, toJSON: () => ({}) });
    fireEvent.click(screen.getByRole("button", { name: "확대" }));
    fireEvent.pointerDown(surface, { clientX: 10, clientY: 20, pointerId: 1 });
    fireEvent.pointerMove(surface, { clientX: 110, clientY: 70, pointerId: 1 });
    fireEvent.pointerUp(surface, { clientX: 110, clientY: 70, pointerId: 1 });
    await new Promise((resolve) => window.setTimeout(resolve, 0));
    fireEvent.click(surface, { clientX: 310, clientY: 270 });
    fireEvent.click(surface, { clientX: 310, clientY: 270 });
    expect(onPointAdd).toHaveBeenCalledWith({ x: 191, y: 200 });
  });
});
