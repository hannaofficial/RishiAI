# 🌿 Rishi.AI — Calm Stories & Wise Guidance  
*A 24-hour hackathon prototype*


## 🌺 Find Clarity Through Ancient Wisdom

What’s weighing on your mind today — a tough life decision, endless overthinking, stress, or quiet anxiety you can’t put into words?

Here, we listen — not just to your problems, but to the patterns beneath them. Once you share what you’re going through, we’ll find a story from the ancient Indian texts — the Upanishads, the Mahabharata, the Yoga Sutras, or timeless folk wisdom — that mirrors your experience.

Through that story, you’ll begin to see your life from a new lens — one that brings peace, perspective, and understanding. You’ll not only find the message the rishis left behind, but also a guide tailored to your way of thinking and your path of growth — helping you dive deep into the root cause of your thoughts, emotions, and patterns.

**Our purpose is simple yet profound:**
✨ To help you find clarity.
✨ To turn confusion into calm.
✨ To help you act without overthinking — and live in alignment with your true self.

Because sometimes, what you need isn’t advice — it’s a story that awakens the truth already within you. 🌿
---

## ✨ What is Rishi.AI?

Rishi.AI is a calm, non-judgmental companion designed to help people dealing with **anxiety, stress, or overthinking**.

You speak in simple English →  
Rishi.AI retrieves wisdom from **Indian texts** (starting with the *Bhagavad Gītā*) →  
It creates a **short calming story** with gentle next steps.

This is not therapy or medical advice — it’s a **reflection-based guidance experience** rooted in clarity and ancient wisdom.

---

## 🌱 Why this matters

Modern world = more information + more opportunity  
But also = **more anxiety, restlessness, overthinking**

Ancient Indian wisdom focused on:

- Steadying the mind 🧘‍♂️  
- Clear action without attachment 🎯  
- Freedom from mental noise 🕊️  

But the wisdom is **scattered**, **dense**, and hard to apply *in the moment*.

> Rishi.AI converts that timeless wisdom into  
**short stories + gentle next steps that you can apply today.**

---

## 🧠 How it Works (Demo Flow)

1. **Express** — User shares what’s bothering them  
2. **Agents at Work** (progress visibly streams on UI):
   - 🔎 **RAG** → search scripture (*Bhagavad Gītā*)
   - 🌐 **Web (optional)** → fetch factual context or grounding
   - ✨ **Curate** → merge scripture + insight
   - ✍️ **LLM** → writes a short calming story + takeaways (with emojis)

3. **Story Experience**
   - Slides (static images for prototype)
   - Narration text
   - Pull-out takeaways
   - Verse citations

4. **Guide Chat**
   - Choose a persona (e.g., Krishna, J. Krishnamurti, Patanjali)
   - Ask questions and get kind, reflective answers  
   *(mocked in prototype)*

5. **Practices**
   - Tiny, actionable practices (breathing, awareness, tiny action)

6. **Karmic Points**
   - Lightweight progress framing

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React, Tailwind CSS, SSE for live progress |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic |
| **Database** | PostgreSQL (psycopg) |
| **RAG** | ChromaDB + Sentence Transformers (`all-MiniLM-L6-v2`) |
| **LLM** | Google Gemini (warm + emoji story generation) |
| **Search (Optional)** | OpenRouter (Perplexity Sonar search) |
| **Agents** | Minimal “agent functions” (later swappable to CrewAI/LangGraph) |
| **TTS** | Deferred; UI supports narration text |

---

