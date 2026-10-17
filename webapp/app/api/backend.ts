import { getChatGPTUser } from "../chatgpt-auth";

export async function backend(path: string, init: RequestInit = {}) {
  if (!(await getChatGPTUser())) return Response.json({ error: "Sign in to use this private studio." }, { status: 401 });
  const url = process.env.OPENJUTSU_BACKEND_URL;
  const key = process.env.OPENJUTSU_API_KEY;
  if (!url || !key) return Response.json({ error: "The generation backend has not been configured." }, { status: 503 });
  try {
    const endpoint = new URL(path, url.endsWith("/") ? url : url + "/");
    const localDev = process.env.NODE_ENV === "development" && endpoint.protocol === "http:" && ["localhost","127.0.0.1"].includes(endpoint.hostname);
    if (endpoint.protocol !== "https:" && !localDev) throw new Error("Invalid backend configuration");
    const response = await fetch(endpoint, {
      ...init,
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      signal: AbortSignal.timeout(35000),
    });
    const value = await response.json() as Record<string, unknown>;
    if (!response.ok) return Response.json({ error: typeof value.detail === "string" ? value.detail : "The generation service could not handle this request." }, { status: response.status, headers: { "Cache-Control": "no-store" } });
    return Response.json(value, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return Response.json({ error: "The generation service is temporarily unavailable. Please check again." }, { status: 502 });
  }
}
