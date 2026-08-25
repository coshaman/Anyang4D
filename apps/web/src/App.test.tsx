import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

afterEach(() => vi.unstubAllGlobals());

describe("SAFE-Twin real citizen shell", () => {
  it("loads the real facility counts and keeps provenance visible", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "안양 재난 대응 지도" })).toBeInTheDocument();
    expect(screen.getByText("공식 데이터 기준")).toBeInTheDocument();
    expect(screen.getByText(/대피소\s*231곳/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "AED" })).toBeInTheDocument();
    expect(screen.queryByText("테스트용 예시 데이터")).not.toBeInTheDocument();
  });

  it("opens the AED flow with 119 as the first action", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "AED" }));
    fireEvent.click(await screen.findByRole("button", { name: "AED 찾기" }));

    expect(screen.getAllByRole("link", { name: /119 신고/ })[0]).toHaveAttribute("href", "tel:119");
    expect(screen.getByText(/AED 원문에는 좌표가 없습니다/)).toBeInTheDocument();
  });

  it("opens a clearly labeled citizen training preview backed by a real scenario frame", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ items: [{ scenario_id: "anyang-general-evacuation-competition", title: "안양 일반 대피 훈련", disaster_type: "GENERAL_EVACUATION", frame_times: [0, 10] }] }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ scenario_id: "anyang-general-evacuation-competition", time_minute: 0, hazard: { geometry: null, label: null, provenance: "ADMIN_SCENARIO" }, roads: { changed_count: 0, changed: [] }, facilities: [], available_shelter_count: 231, assignment: { evacuation_demand: 100, assigned: 100, unserved: 0, average_assigned_travel_distance_m: 120 }, terrain_authorized: false, citizen_guidance_authorized: false, computation_status: "READY" }), { status: 200 })));

    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "재난 상황 미리보기" }));

    expect(await screen.findByRole("heading", { name: "재난 상황 미리보기" })).toBeInTheDocument();
    expect(await screen.findByText("안양 일반 대피 훈련")).toBeInTheDocument();
    expect(screen.getByText(/훈련\/가정 시나리오/)).toBeInTheDocument();
    expect(await screen.findByText(/대피 수요/)).toBeInTheDocument();
  });

  it("supports large text mode", () => {
    render(<App />);
    screen.getByRole("button", { name: "큰 글씨" }).click();
    expect(document.documentElement).toHaveAttribute("data-text-size", "large");
  });

  it("shows administrative what-if controls without citizen hazard claims", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "관리자 시뮬레이터" }));
    expect(await screen.findByRole("heading", { name: "안양 4D 도시상태 시뮬레이터" })).toBeInTheDocument();
    expect(screen.getByText("훈련/가정 시나리오")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "현재 시간에 hazard keyframe 추가" })).toBeInTheDocument();
    expect(screen.getByText(/시민 emergency routing이 아닙니다/)).toBeInTheDocument();
  });
});
