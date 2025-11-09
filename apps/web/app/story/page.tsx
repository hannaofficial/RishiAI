"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { postJSON } from "../../lib/api";
import { Howl } from "howler";

type Slide = { image_url: string; caption: string };
type Citation = { work: string; ref?: string };
type Story = {
  title: string;
  slides: Slide[];
  narration_text: string;
  takeaways: string[];
  citations: Citation[];
  audio_url?: string | null;
  bg_music_url?: string | null;
};

export default function StoryPage() {
  const [story, setStory] = useState<Story | null>(null);
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [bgOn, setBgOn] = useState(true);
  const [qa, setQa] = useState("");
  const [qaAnswer, setQaAnswer] = useState("");

  const bgRef = useRef<Howl | null>(null);
  const narRef = useRef<Howl | null>(null);
  const ttsRef = useRef<SpeechSynthesisUtterance | null>(null);
  const slideTimer = useRef<NodeJS.Timeout | null>(null);

  // Load story from session
  useEffect(() => {
    const cached = sessionStorage.getItem("story_payload");
    if (cached) setStory(JSON.parse(cached));
  }, []);

  // Preload images
  useEffect(() => {
    if (!story?.slides) return;
    story.slides.forEach(s => {
      const img = new Image();
      img.src = s.image_url;
    });
  }, [story?.slides]);

  // Setup BG music (Howler)
  useEffect(() => {
    if (!story?.bg_music_url) return;
    if (bgRef.current) {
      bgRef.current.unload();
      bgRef.current = null;
    }
    bgRef.current = new Howl({ src: [story.bg_music_url], loop: true, volume: 0.25 });
    if (bgOn) bgRef.current.play();
    return () => { bgRef.current?.unload(); bgRef.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [story?.bg_music_url]);

  // Toggle BG music
  useEffect(() => {
    if (!bgRef.current) return;
    if (bgOn) bgRef.current.play();
    else bgRef.current.pause();
  }, [bgOn]);

  // Auto-advance slides
  useEffect(() => {
    if (!story?.slides?.length) return;
    if (slideTimer.current) clearInterval(slideTimer.current);
    slideTimer.current = setInterval(() => {
      setIdx(i => (story.slides ? (i + 1) % story.slides.length : i));
    }, 6000);
    return () => { if (slideTimer.current) clearInterval(slideTimer.current); };
  }, [story?.slides?.length]);

  // Narration: prefer server audio_url (Howler). If absent, use browser TTS.
  function playNarration() {
    if (!story) return;
    stopNarration(); // clean any existing

    if (story.audio_url) {
      narRef.current = new Howl({ src: [story.audio_url], html5: true, volume: 1.0 });
      narRef.current.play();
      setPlaying(true);
      narRef.current.once("end", () => setPlaying(false));
    } else if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(story.narration_text);
      u.rate = 0.95; u.pitch = 1.0; u.lang = "en-US";
      u.onend = () => setPlaying(false);
      ttsRef.current = u;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
      setPlaying(true);
    } else {
      alert("Narration not available on this browser.");
    }
  }

  function pauseNarration() {
    if (narRef.current) {
      narRef.current.pause();
      setPlaying(false);
      return;
    }
    if (ttsRef.current && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      setPlaying(false);
    }
  }

  function resumeNarration() {
    if (narRef.current) {
      narRef.current.play();
      setPlaying(true);
      return;
    }
    if (ttsRef.current && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      setPlaying(true);
    }
  }

  function stopNarration() {
    if (narRef.current) { narRef.current.stop(); narRef.current.unload(); narRef.current = null; }
    if (ttsRef.current) { window.speechSynthesis.cancel(); ttsRef.current = null; }
    setPlaying(false);
  }

  async function askStoryQA() {
    setQaAnswer("Thinking…");
    const data = await postJSON<{ answer_text: string; citations: Citation[] }>("/story/qa", {
      story_id: "demo-story",
      question: qa,
    });
    setQaAnswer(data.answer_text);
  }

  if (!story) return <main className="max-w-3xl mx-auto p-6">Loading story…</main>;

  const slides = story.slides || [];
  const current = slides[idx] || slides[0];
  const progress = slides.length ? Math.round(((idx + 1) / slides.length) * 100) : 0;

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-semibold">{story.title}</h2>

      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-200 rounded">
        <div className="h-2 bg-sky-500 rounded" style={{ width: `${progress}%` }} />
      </div>

      {/* Slide */}
      <div className="border rounded-lg overflow-hidden">
        <img
          src={current?.image_url}
          alt=""
          className="w-full h-[360px] object-cover"
        />
        <div className="p-3 text-sm opacity-80">{current?.caption}</div>
      </div>

      {/* Narration & BG controls */}
      <div className="flex flex-wrap items-center gap-2">
        {!playing ? (
          <button onClick={playNarration} className="px-3 py-2 rounded bg-sky-600 text-white hover:bg-sky-700">
            ▶ Play narration
          </button>
        ) : (
          <div className="flex gap-2">
            <button onClick={pauseNarration} className="px-3 py-2 rounded bg-gray-200">⏸ Pause</button>
            <button onClick={resumeNarration} className="px-3 py-2 rounded bg-gray-200">▶ Resume</button>
            <button onClick={stopNarration} className="px-3 py-2 rounded bg-gray-200">⏹ Stop</button>
          </div>
        )}

        <label className="ml-3 inline-flex items-center gap-2">
          <input type="checkbox" checked={bgOn} onChange={(e) => setBgOn(e.target.checked)} />
          <span>BG music</span>
        </label>
      </div>

      {/* Narration text */}
      <p className="text-lg">{story.narration_text}</p>

      {/* Takeaways */}
      <div>
        <b>Takeaways:</b>
        <ul className="list-disc pl-6">
          {story.takeaways?.map((t, i) => <li key={i}>{t}</li>)}
        </ul>
      </div>

      {/* Citations */}
      <div className="opacity-80">
        <b>Citations:</b>{" "}
        {story.citations?.map((c, i) => (
          <span key={i}>
            {c.work}{c.ref ? ` ${c.ref}` : ""}
            {i < story.citations.length - 1 ? ", " : ""}
          </span>
        ))}
      </div>

      <hr className="my-2" />

      {/* Story Q&A */}
      <section>
        <h3 className="text-xl font-semibold">Ask about this story 📖</h3>
        <div className="mt-2 flex gap-2">
          <input
            value={qa}
            onChange={(e) => setQa(e.target.value)}
            placeholder="What does this mean for me?"
            className="w-full rounded border px-3 py-2"
          />
          <button onClick={askStoryQA} className="px-3 py-2 rounded bg-gray-100 hover:bg-gray-200">
            Ask
          </button>
        </div>
        {qaAnswer && <p className="mt-2">{qaAnswer}</p>}
      </section>

      <div className="mt-2">
        <a href="/guide" className="inline-block rounded border px-4 py-2 hover:bg-gray-50">
          Talk to a Guide →
        </a>
      </div>
    </main>
  );
}
