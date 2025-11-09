const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function postJSON<T>(path: string, body: any): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function getOrCreateUserId(): string {
  if (typeof window === "undefined") return "demo-user";
  const key = "demo_user_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export async function fetchPractices(user_id: string, emotion_tags: string[] = ["anxiety"]) {
  return postJSON<{ practices: { title:string; why:string; roots:string; steps:string[] }[] }>(
    "/practice/suggest",
    { user_id, emotion_tags }
  );
}

