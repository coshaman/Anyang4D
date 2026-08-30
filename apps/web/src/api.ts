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

export async function fetchJson<T>(endpoint: string, init: RequestInit = {}, timeoutMs = 12000, retries = 1): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(endpoint, { ...init, signal: controller.signal });
      return await readJsonResponse<T>(response, endpoint);
    } catch (error) {
      lastError = error instanceof DOMException && error.name === "AbortError"
        ? new Error(`서버 응답 시간 초과 · ${endpoint}`)
        : error;
      if (attempt === retries) throw lastError;
    } finally {
      window.clearTimeout(timeout);
    }
  }
  throw lastError instanceof Error ? lastError : new Error(`서버 연결 오류 · ${endpoint}`);
}
