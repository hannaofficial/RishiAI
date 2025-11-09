"use client";
import { useEffect, useState } from "react";
import { fetchPractices } from "../../lib/api";
import { getOrCreateUserId } from "../../lib/api";

type Practice = { title:string; why:string; roots:string; steps:string[] };

export default function PracticesPage() {
  const [items, setItems] = useState<Practice[]>([]);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState<string>("");

  useEffect(() => {
    const user_id = getOrCreateUserId();
    // For demo, try to read any emotion tags you may have saved earlier; else default
    const tags = JSON.parse(sessionStorage.getItem("emotion_tags") || '["anxiety"]');
    fetchPractices(user_id, tags)
      .then((res) => setItems(res.practices || []))
      .finally(() => setLoading(false));
  }, []);

  function onAction(kind: "save" | "try" | "skip", p: Practice) {
    // Demo: pretend to record the click; show a tiny note
    const msg =
      kind === "save"
        ? `Saved: ${p.title}`
        : kind === "try"
        ? `Great choice. Try: ${p.title} 💙`
        : `Noted. We'll suggest other options.`;
    setNote(msg);
    setTimeout(() => setNote(""), 2000);
  }

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto p-6">
        <h2 className="text-2xl font-semibold">Try these calm practices 🌿</h2>
        <p className="opacity-70 mt-2">Finding gentle steps for you…</p>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-semibold">Try these calm practices 🌿</h2>
      <p className="opacity-70 mt-2">Simple steps. Kind pace. You choose.</p>

      <div className="mt-4 space-y-4">
        {items.map((p, i) => (
          <div key={i} className="border rounded-lg p-4">
            <h3 className="text-lg font-medium">{p.title}</h3>
            <p className="mt-1">{p.why}</p>
            <p className="mt-1"><b>Roots:</b> {p.roots}</p>
            <p className="mt-1"><b>Steps:</b> {p.steps.join(" • ")}</p>

            <div className="mt-3 flex gap-2">
              <button
                onClick={() => onAction("save", p)}
                className="px-3 py-2 rounded bg-gray-100 hover:bg-gray-200"
              >
                Save
              </button>
              <button
                onClick={() => onAction("try", p)}
                className="px-3 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700"
              >
                I’ll try
              </button>
              <button
                onClick={() => onAction("skip", p)}
                className="px-3 py-2 rounded bg-gray-100 hover:bg-gray-200"
              >
                Not for me
              </button>
            </div>
          </div>
        ))}
      </div>

      {note && <div className="mt-4 text-sm text-emerald-700">{note}</div>}

      <div className="mt-6">
        <a
          href="/progress"
          className="inline-block px-4 py-2 border rounded hover:bg-gray-50"
        >
          Next → Progress
        </a>
      </div>
    </main>
  );
}
