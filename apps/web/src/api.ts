export const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? "http://127.0.0.1:8000/api" : "/api");

export async function readJsonResponse<T>(response: Response, endpoint: string): Promise<T> {
  const body = await response.text();
  if (!response.ok) {
    throw new Error(`서버 연결 오류 · ${endpoint} · HTTP ${response.status}`);
  }
  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (!contentType.includes("application/json") && !/^[\s]*[\[{]/.test(body)) {
    throw new Error(`서버 응답 형식 오류 · ${endpoint} · HTTP ${response.status}`);
  }
  try {
    return JSON.parse(body) as T;
  } catch {
    throw new Error(`서버 응답 형식 오류 · ${endpoint} · HTTP ${response.status}`);
  }
}
