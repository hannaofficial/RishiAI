"use client";
import { useEffect, useState } from "react";
import { getOrCreateUserId } from "../../lib/api";

export default function ProgressPage() {
  const [data, setData] = useState<{karmic_points:number; streak_days:number; level:string} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user_id = getOrCreateUserId();
    fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/progress?user_id=${user_id}`)
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <main className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-semibold">Your gentle progress</h2>
      <p className="opacity-70 mt-2">Loading…</p>
    </main>
  );

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-semibold">Your gentle progress</h2>
      <div className="border rounded-lg p-4 mt-3">
        <p><b>Karmic points:</b> {data?.karmic_points ?? 0} ✨</p>
        <p><b>Streak:</b> {data?.streak_days ?? 0} days</p>
        <p><b>Level:</b> {data?.level ?? "Starter"}</p>
      </div>
      <p className="mt-4">
        You came this far. Talking is brave. Next time, tell me one action you tried. I will guide you. 🌱
      </p>
      <div className="mt-6">
        <a href="/" className="inline-block px-4 py-2 border rounded hover:bg-gray-50">Start again →</a>
      </div>
    </main>
  );
}
