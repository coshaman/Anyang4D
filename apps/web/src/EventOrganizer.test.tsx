import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EventOrganizer } from "./EventOrganizer";
import { FloorPlanCanvas } from "./FloorPlanCanvas";

describe("event organizer workflow", () => {
  it("creates an event plan from name, venue, and indoor representation", () => {
    const onPreview = vi.fn();
    render(<EventOrganizer onPreview={onPreview} />);
    fireEvent.change(screen.getByLabelText("행사명"), { target: { value: "안양 해커톤" } });
    fireEvent.change(screen.getByLabelText("행사 장소"), { target: { value: "안양대학교 강당" } });
    fireEvent.click(screen.getByRole("button", { name: "다음" }));
    fireEvent.click(screen.getByLabelText("실내 도면"));
    fireEvent.click(screen.getByRole("button", { name: "계획 미리보기" }));
    expect(onPreview).toHaveBeenCalledWith(expect.objectContaining({ name: "안양 해커톤", venue: "안양대학교 강당", representation: "INDOOR" }));
  });

  it("emits image-local coordinates when the floor plan is clicked", () => {
    const onPointAdd = vi.fn();
    render(<FloorPlanCanvas width={400} height={300} onPointAdd={onPointAdd} points={[]} route={[]} />);
    fireEvent.click(screen.getByTestId("floor-plan-surface"), { clientX: 100, clientY: 75 });
    expect(onPointAdd).toHaveBeenCalledWith({ x: 100, y: 75 });
  });
});
