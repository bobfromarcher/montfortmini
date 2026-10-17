import { backend } from "../backend";
import { getChatGPTUser } from "../../chatgpt-auth";

export async function POST(request: Request) {
  if (!(await getChatGPTUser())) return Response.json({ error: "Sign in to use this private studio." }, { status: 401 });
  if (!request.body) return Response.json({ error: "Select a video and reference first." }, { status: 400 });
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 24 * 1024 * 1024) {
      await reader.cancel();
      return Response.json({ error: "This upload exceeds the prototype's size limit." }, { status: 413 });
    }
    chunks.push(value);
  }
  const body = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
  return backend("jobs", { method: "POST", body });
}

export async function GET(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (!id || id.length > 200) return Response.json({ error: "Invalid job identifier." }, { status: 400 });
  return backend(`jobs?id=${encodeURIComponent(id)}`);
}
