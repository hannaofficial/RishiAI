"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { postJSON, getOrCreateUserId } from "../lib/api";

type StreamEvent =
  | { stage: "router" | "rag" | "search" | "llm"; msg: string }
  | { stage: "done"; msg: string; story_payload: any; session_id?: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ExpressPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // A simple staged fallback ticker in case streaming fails
  const tickerRef = useRef<NodeJS.Timeout | null>(null);
  function startFallbackTicker() {
    const steps = [
      "🧠 Understanding your problem…",
      "🔎 Checking Bhagavad Gita (RAG)…",
      "🌐 Looking up helpful references…",
      "✍️ Writing your story…",
    ];
    let i = 0;
    setProgress([steps[0]]);
    tickerRef.current = setInterval(() => {
      i = (i + 1) % steps.length;
      setProgress((prev) => {
        const copy = prev.slice();
        copy[copy.length - 1] = steps[i];
        return copy;
      });
    }, 1200);
  }
  function stopFallbackTicker() {
    if (tickerRef.current) {
      clearInterval(tickerRef.current);
      tickerRef.current = null;
    }
  }

  async function handleStreamStory(user_id: string, emotionTags: string[]) {
    // Try to stream progress + story from /story/stream
    const body = JSON.stringify({
      user_id,
      problem_text: text,
      language: "en",
      sources: ["auto"],
      emotion_tags: emotionTags,
    });

    const res = await fetch(`${API_BASE}/story/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    if (!res.ok || !res.body) {
      throw new Error(`stream unavailable (${res.status})`);
    }

    // Parse text/event-stream manually
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    // show initial line
    setProgress((p) => (p.length ? p : ["🧠 Understanding your problem…"]));

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Split on SSE event boundaries
      const events = buffer.split("\n\n");
      // keep last partial chunk in buffer
      buffer = events.pop() || "";

      for (const evt of events) {
        const line = evt.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        const jsonStr = line.slice(6);
        let data: StreamEvent | null = null;
        try {
          data = JSON.parse(jsonStr);
        } catch {
          continue;
        }
        if (!data) continue;

        if (data.stage !== "done") {
          setProgress((prev) => [...prev, data.msg]);
        } else {
          // Final payload from stream
          if (data.story_payload) {
            sessionStorage.setItem(
              "story_payload",
              JSON.stringify(data.story_payload)
            );
          }
          if (data.session_id) {
            sessionStorage.setItem("session_id", data.session_id);
          }
          stopFallbackTicker();
          return; // success
        }
      }
    }

    // If we exit the loop without a done, treat as failure
    throw new Error("stream ended without 'done'");
  }

  async function handlePersistStory(user_id: string, emotionTags: string[]) {
    // Fallback or post-stream: ensure backend has a session_id persisted
    const resp = await postJSON<{ story: any; session_id: string }>(
      `${API_BASE}/story`,
      {
        user_id,
        problem_text: text,
        language: "en",
        sources: ["auto"],
        emotion_tags: emotionTags,
      }
    );
    if (resp?.story) {
      sessionStorage.setItem("story_payload", JSON.stringify(resp.story));
    }
    if (resp?.session_id) {
      sessionStorage.setItem("session_id", resp.session_id);
    }
  }

  async function onContinue() {
    setError(null);
    if (!text.trim()) return;

    setBusy(true);
    setProgress([]);
    startFallbackTicker();

    // Save quick client hints
    const emotionTags = ["anxiety", "overthinking"];
    sessionStorage.setItem("emotion_tags", JSON.stringify(emotionTags));
    sessionStorage.setItem("problem_text", text);

    const user_id = getOrCreateUserId();

    try {
      // Prefer streaming progress if available
      await handleStreamStory(user_id, emotionTags).catch(async () => {
        // No stream? fall back to regular /story
        await handlePersistStory(user_id, emotionTags);
      });

      // If stream didn’t include a session, persist now (idempotent; backend will handle duplicates)
      const maybeSession = sessionStorage.getItem("session_id");
      if (!maybeSession) {
        await handlePersistStory(user_id, emotionTags);
      }

      stopFallbackTicker();
      setBusy(false);
      router.push("/story");
    } catch (e: any) {
      stopFallbackTicker();
      setBusy(false);
      setError(
        e?.message
          ? `Something went wrong: ${e.message}`
          : "Something went wrong creating your story."
      );
    }
  }

  // Clean up ticker on unmount
  useEffect(() => {
    return () => stopFallbackTicker();
  }, []);

  return (
    <main className="mx-auto max-w-2xl p-4 sm:p-6">
      <h1 className="text-2xl font-semibold tracking-tight">
        Tell me what is on your mind. I am here. 💙
      </h1>
      <p className="mt-1 text-sm text-neutral-600">
        Simple words are okay. I will not judge.
      </p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        placeholder="Write here..."
        className="mt-4 w-full resize-y rounded-lg border border-neutral-300 p-3 text-base outline-none ring-0 focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
      />

      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={onContinue}
          disabled={busy || !text.trim()}
          className="inline-flex items-center rounded-lg bg-sky-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50 hover:bg-sky-700"
        >
          {busy ? "Working…" : "Continue →"}
        </button>

        {busy && (
          <span className="text-sm text-neutral-500">
            Finding the best story for you…
          </span>
        )}
      </div>

      {busy && (
        <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm">
          <ul className="list-disc pl-5 space-y-1">
            {progress.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Dev helper: visual responsive hint */}
      <div className="mt-6 rounded-lg border-4 border-red-500 p-3 md:border-green-500">
        Resize the window: red border on mobile, green on desktop.
      </div>
    </main>
  );
}
