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
});
