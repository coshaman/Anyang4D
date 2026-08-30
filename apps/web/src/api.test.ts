import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchJson, readJsonResponse } from "./api";

describe("readJsonResponse", () => {
  afterEach(() => vi.restoreAllMocks());
  it("reports a concise endpoint error for an empty 502 response", async () => {
    const response = new Response("", { status: 502 });
    await expect(readJsonResponse(response, "/api/release/readiness")).rejects.toThrow(
      "서버 연결 오류 · /api/release/readiness · HTTP 502",
    );
  });

  it("does not parse a non-JSON successful response as JSON", async () => {
    const response = new Response("upstream text", { status: 200, headers: { "content-type": "text/plain" } });
    await expect(readJsonResponse(response, "/api/release/version")).rejects.toThrow(
      "서버 응답 형식 오류 · /api/release/version · HTTP 200",
    );
  });

  it("retries a failed JSON request once", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockRejectedValueOnce(new Error("temporary network failure"))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "content-type": "application/json" } }));
    await expect(fetchJson<{ ok: boolean }>("/api/routes", {}, 100, 1)).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("turns an aborted request into a bounded timeout error", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
    }));
    await expect(fetchJson("/api/routes", {}, 1, 0)).rejects.toThrow("서버 응답 시간 초과");
  });
});
