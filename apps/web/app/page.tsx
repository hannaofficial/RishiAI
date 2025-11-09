"use client";
import { useState } from "react";
import { postJSON, getOrCreateUserId } from "../lib/api";
import { useRouter } from "next/navigation";

export default function ExpressPage() {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function onContinue() {
    if (!text.trim()) return;
    setBusy(true);
    sessionStorage.setItem("emotion_tags", JSON.stringify(["anxiety","overthinking"]));
    const user_id = getOrCreateUserId();
    sessionStorage.setItem("problem_text", text);
    const data = await postJSON<{story:any; session_id:string}>("/story", {
  user_id, problem_text: text, language: "en", sources: ["auto"], emotion_tags: ["anxiety", "overthinking"],
    });
    sessionStorage.setItem("story_payload", JSON.stringify(data.story));
    sessionStorage.setItem("session_id", data.session_id); // 
        setBusy(false);
        router.push("/story");
    }

  return (
    <main className="mx-auto max-w-2xl p-4 sm:p-6">
      {/* SMOKE TEST BANNER */}
      {/* <div className="mb-4 rounded-lg bg-gradient-to-r from-fuchsia-500 to-sky-500 p-3 text-white shadow">
        Tailwind is active if you see this gradient box 🎉
      </div> */}

      <h1 className="text-2xl font-semibold tracking-tight">
        Tell me what is on your mind. I am here. 💙
      </h1>
      <p className="mt-1 text-sm text-neutral-600">
        Simple words are fine. I will not judge.
      </p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        placeholder="Write here..."
        className="mt-4 w-full resize-y rounded-lg border border-neutral-300 p-3 text-base outline-none ring-0 focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
      />

      <button
        onClick={onContinue}
        disabled={busy || !text.trim()}
        className="mt-3 inline-flex items-center rounded-lg bg-sky-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50 hover:bg-sky-700"
      >
        {busy ? "Please wait..." : "Continue →"}
      </button>

      {/* RESPONSIVE TEST: border changes color on md+ */}
      <div className="mt-6 rounded-lg border-4 border-red-500 p-3 md:border-green-500">
        Resize the window: red border on mobile, green on desktop.
      </div>
    </main>
  );
}
