import { describe, expect, it } from "vitest";
import { readJsonResponse } from "./api";

describe("readJsonResponse", () => {
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
});
