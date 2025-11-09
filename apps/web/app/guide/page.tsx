"use client";
import { useEffect, useState } from "react";
import { postJSON, getOrCreateUserId } from "../../lib/api";

type Citation = { work: string; ref?: string };
type Reply = {
  reply_text: string;
  questions: string[];
  citations: Citation[];
  persona_selected: string;
};

export default function GuidePage() {
  const [persona, setPersona] = useState<string>("omniphilosopher");
  const [msg, setMsg] = useState("");
  const [log, setLog] = useState<{ role: "user" | "guide"; text: string }[]>(
    []
  );
  const [sessionId, setSessionId] = useState<string>("");

  // Read session_id once on mount
  useEffect(() => {
    const sid = sessionStorage.getItem("session_id") || "";
    setSessionId(sid);
  }, []);

  async function send() {
    if (!msg.trim()) return;
    if (!sessionId) {
      setLog((l) => [
        ...l,
        { role: "guide", text: "Please create a story first, then come back. 💙" },
      ]);
      return;
    }

    const user_id = getOrCreateUserId();

    // append user turn
    setLog((l) => [...l, { role: "user", text: msg }]);
    const outgoing = msg;
    setMsg("");

    // call backend
    const data = await postJSON<Reply>("/guide/chat", {
      session_id: sessionId, // ✅ use the stored session id
      persona,
      message: outgoing,
      language: "en",
    });

    // append guide turn
    setLog((l) => [...l, { role: "guide", text: data.reply_text }]);
  }

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-semibold">Talk to a Guide</h2>

      {!sessionId && (
        <div className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-amber-900">
          No session found. Please start from the story step first.{" "}
          <a className="underline" href="/">
            Go to start →
          </a>
        </div>
      )}

      <div className="mt-3">
        <label className="mr-2">Guide:</label>
        <select
          value={persona}
          onChange={(e) => setPersona(e.target.value)}
          className="rounded border px-2 py-1"
        >
          <option value="omniphilosopher">Omniphilosopher (default)</option>
          <option value="krishna">Krishna</option>
          <option value="jiddu">Jiddu Krishnamurti</option>
          <option value="patanjali">Patanjali</option>
        </select>
      </div>

      <div className="mt-3 min-h-[200px] rounded-lg border p-3">
        {log.map((m, i) => (
          <p key={i} className={m.role === "guide" ? "" : "opacity-90"}>
            <b>{m.role === "guide" ? "Guide" : "You"}:</b> {m.text}
          </p>
        ))}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          placeholder="Say what is on your mind..."
          className="w-[70%] rounded border px-3 py-2"
        />
        <button
          onClick={send}
          className="rounded bg-sky-600 px-4 py-2 text-white hover:bg-sky-700 disabled:opacity-50"
          disabled={!msg.trim()}
        >
          Send
        </button>
      </div>

      <div className="mt-6">
        <a
          href="/practices"
          className="inline-block rounded border px-4 py-2 hover:bg-gray-50"
        >
          See calming practices →
        </a>
      </div>
    </main>
  );
}
