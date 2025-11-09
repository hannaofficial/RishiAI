from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    StoryRequest, StoryResponse, StoryPayload, Slide, Citation,
    StoryQARequest, StoryQAResponse,
    GuideChatRequest, GuideChatResponse, PracticeSuggestRequest, PracticeSuggestResponse, PracticeItem
)

from fastapi import Depends , Query
from sqlalchemy.orm import Session as SASession
from db import get_db
from models_db import User, Session as DBSession, Story as DBStory, Totals
from rag.retrieve import search_gita

from memory.user_memory import summarize_if_needed
from persona_router import choose_persona

import os, hashlib, pathlib, asyncio
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks
app = FastAPI(title="Rishi.AI Orchestrator")

STATIC_DIR = os.getenv("STATIC_DIR", "./static")
os.makedirs(os.path.join(STATIC_DIR, "tts"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


MIN_VALID_BYTES = 4096


# Allow local Next.js to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STYLE_NOTE = (
    "Simple English. Kind and calm. At most 2 gentle emojis. "
    "No medical or legal advice."
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/story", response_model=StoryResponse)
def create_story(req: StoryRequest, db: SASession = Depends(get_db)):
    # 1) Upsert user and award courage bonus on first sighting
    user = db.get(User, req.user_id)
    if not user:
        user = User(id=req.user_id)
        db.add(user)
        db.flush()
        db.add(Totals(user_id=user.id, karmic_points=15))  # courage bonus

    # 2) Create a session (store emotion tags if provided)
    sess = DBSession(
        user_id=user.id,
        problem_text=req.problem_text,
        emotion_tags=(req.emotion_tags or ["anxiety", "overthinking"]),
        last_stage="story",
    )
    db.add(sess); db.flush()

    # 3) Try RAG (Gita) first
    hits = []
    try:
        hits = search_gita(req.problem_text, k=3)
    except Exception:
        hits = []

    if hits:
        # Use top hit’s citation
        top = hits[0]["meta"] or {}
        work = top.get("work", "Bhagavad Gita")
        chapter = top.get("chapter")
        verse = top.get("verse")
        ref = f"{chapter}.{verse}" if chapter and verse else None

        story_payload = StoryPayload(
            title="Do Your Part. Let Worry Be Light.",
            slides=[
                Slide(image_url="/assets/kurukshetra_1.jpg", caption="Arjuna feels fear on the field."),
                Slide(image_url="/assets/krishna_guides.jpg", caption="Krishna speaks with care."),
            ],
            narration_text=(
                "This teaching is simple: do your action. Do not hold the result too tight. "
                "Take one small step today. 💙"
            ),
            takeaways=[
                "Do one tiny step today. 🌱",
                "Breathe slow before you act.",
                "Let results be light."
            ],
            citations=[Citation(work=work, ref=ref)]
        )
    else:
        # 4) Fallback: your original friendly mock
        story_payload = StoryPayload(
            title="Do Your Part. Let Worry Be Light.",
            slides=[
                Slide(image_url="/assets/kurukshetra_1.jpg", caption="Arjuna feels fear on the field."),
                Slide(image_url="/assets/krishna_guides.jpg", caption="Krishna speaks with care."),
            ],
            narration_text=(
                "You feel heavy because you hold the result too tight. "
                "Take one small action. Leave the outcome to time. 💙 "
                "Your step today is enough."
            ),
            takeaways=[
                "Do one tiny step today. 🌱",
                "Breathe slow before you act.",
                "Let results be light."
            ],
            citations=[Citation(work="Bhagavad Gita", ref="2.47")]
        )

    story_payload.bg_music_url = "/audio/bg.mp3"

    # 5) Persist story record
    db.add(DBStory(
        user_id=user.id,
        session_id=sess.id,
        story_json=story_payload.model_dump(),
        citations_json=[c.model_dump() for c in story_payload.citations]
    ))
    db.commit()

    # 6) Return story + session_id so /guide/chat can use it
    return StoryResponse(story=story_payload, session_id=sess.id)


@app.post("/story/qa", response_model=StoryQAResponse)
def story_qa(req: StoryQARequest):
    # Keeps to the story’s idea, asks one gentle question.
    return StoryQAResponse(
        answer_text=(
            "This story teaches: act with a calm mind; let go of results. "
            "Which tiny step fits your life today? ✨"
        ),
        citations=[Citation(work="Bhagavad Gita", ref="2.47")]
    )

@app.post("/guide/chat", response_model=GuideChatResponse)
def guide_chat(req: GuideChatRequest, db: SASession = Depends(get_db)):
    # session_id is required now (from /story response)
    session = db.get(DBSession, req.session_id)
    if not session:
        # If client sent user_id earlier, you could fallback; for now, hard fail for clarity
        raise RuntimeError("Invalid session_id. Create a story first.")

    user = db.get(User, session.user_id)
    if not user:
        raise RuntimeError("User not found for session.")

    # Find last story to infer last_work (for persona router)
    last_story = db.query(DBStory).filter(DBStory.session_id == session.id).order_by(DBStory.created_at.desc()).first()
    last_work = None
    if last_story and last_story.citations_json:
        try:
            # use first citation's work if present
            last_work = (last_story.citations_json[0] or {}).get("work")
        except Exception:
            pass

    # Auto persona if requested
    persona_in = (req.persona or "").lower()
    persona_selected = persona_in
    if persona_in == "auto" or persona_in == "":
        persona_selected = choose_persona(
            emotion_tags=session.emotion_tags,
            last_work=last_work,
            guidance_style=None  # wire real style later
        )

    # --- compose reply (still mock text, but persona-aware) ---
    p = persona_selected
    if p == "krishna":
        text = (
            "Act from a quiet mind. Let results be light. "
            "What small action can you take now, if results did not matter? 💙"
        )
        cites = [Citation(work="Bhagavad Gita", ref="2.47")]
    elif p == "jiddu":
        text = (
            "Can you look at the worry without pushing it away? "
            "Just see it, like a cloud. What do you notice now? 🌱"
        )
        cites = []
    elif p == "patanjali":
        text = (
            "Let us link breath and mind. Take one slow breath. "
            "What tiny step feels kind after that breath?"
        )
        cites = []
    else:
        text = (
            "Thank you for sharing. We will go step by step. "
            "What is one tiny action you can try in 10 minutes?"
        )
        cites = []

    # --- persist chat turn ---
    chat = db.query(DBChat).filter(DBChat.session_id == session.id, DBChat.persona == persona_selected).first()
    if not chat:
        chat = DBChat(user_id=session.user_id, session_id=session.id, persona=persona_selected, turns=[])
        db.add(chat)
        db.flush()

    # append user + guide turns
    turns = chat.turns or []
    turns.append({"role": "user", "text": req.message})
    turns.append({"role": "guide", "text": text})
    chat.turns = turns
    db.add(chat)

    # summarize to user_memory every N turns
    summarize_if_needed(user_id=session.user_id, session_id=session.id, turns=turns, every_n=6)

    db.commit()

    return GuideChatResponse(
        reply_text=text,
        questions=["What is your one tiny step today?"],
        citations=cites,
        persona_selected=persona_selected
    )

@app.post("/practice/suggest", response_model=PracticeSuggestResponse)
def practice_suggest(req: PracticeSuggestRequest):
    # Very simple, emotion-aware branching (demo)
    em = [e.lower() for e in (req.emotion_tags or [])]
    anxious = "anxiety" in em or "overthinking" in em or "stress" in em

    base = [
        PracticeItem(
            title="Box Breathing 4-4-4-4 🫁",
            why="It calms the body and slows racing thoughts. ✨",
            roots="Patanjali • Hatha Yoga (pranayama)",
            steps=["Inhale 4", "Hold 4", "Exhale 4", "Hold 4 (repeat 5 times)"]
        ),
        PracticeItem(
            title="Heart Focus (Dharana) 🕊️",
            why="It anchors your attention. Worry feels smaller.",
            roots="Vigyana Bhairava Tantra",
            steps=["Sit easy", "Place attention at heart", "Breathe soft for 1 minute"]
        ),
    ]

    extra = PracticeItem(
        title="One Tiny Karma Step 🧭",
        why="Action breaks loops. Small steps build trust in yourself.",
        roots="Bhagavad Gītā 2.47 (act, release the fruit)",
        steps=["Pick one 5-minute task", "Do it gently", "Let results be light"]
    )

    practices = base + ([extra] if anxious else [])
    return PracticeSuggestResponse(practices=practices)


class ProgressResponse(BaseModel):
    karmic_points: int
    streak_days: int
    level: str

def level_from_points(points: int) -> str:
    if points >= 200: return "Sage"
    if points >= 120: return "Practitioner"
    if points >= 60:  return "Seeker"
    return "Starter"

@app.get("/progress", response_model=ProgressResponse)
def get_progress(user_id: str = Query(...), db: SASession = Depends(get_db)):
    totals = db.get(Totals, user_id)
    if not totals:
        # create with 15 courage bonus if missing (first-time safeguard)
        totals = Totals(user_id=user_id, karmic_points=15, streak_days=0)
        db.add(totals); db.commit(); db.refresh(totals)
    return ProgressResponse(
        karmic_points=totals.karmic_points or 0,
        streak_days=totals.streak_days or 0,
        level=level_from_points(totals.karmic_points or 0)
    )



# agents planning
class KnowledgePlanRequest(BaseModel):
    problem_text: str
    rag_citations: list[dict] = []

class KnowledgePlanResponse(BaseModel):
    queries: list[str]
    adequate: bool
    reason: str

from agents.search import plan_queries, web_search_stub, adequacy_gate

@app.post("/knowledge/plan", response_model=KnowledgePlanResponse)
def knowledge_plan(req: KnowledgePlanRequest):
    qs = plan_queries(req.problem_text, req.rag_citations)
    snippets = web_search_stub(qs)
    adeq = adequacy_gate(req.problem_text, req.rag_citations, snippets)
    return KnowledgePlanResponse(queries=qs, adequate=adeq["sufficient"], reason=adeq["reason"])


from pydantic import BaseModel, Field

class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str | None = None
    speed: str | None = None
    format: str = "mp3"

class TTSResponse(BaseModel):
    audio_url: str
    voice: str
    speed: str
    format: str
    cached: bool
    provider: str
    size: int


from tts.providers import get_provider, TTS_VOICE, TTS_SPEED, STATIC_DIR, _hash_name,  DummyProvider
import re

def normalize_speed(s: str | None, default: str = "+0%") -> str:
    if not s: s = default
    s = s.strip()
    if re.fullmatch(r"^[+-]\d+%$", s): return s
    if not s.endswith("%"): s = f"{s}%"
    if not (s.startswith("+") or s.startswith("-")): s = f"+{s}"
    if not re.fullmatch(r"^[+-]\d+%$", s): return default
    return s

@app.post("/tts", response_model=TTSResponse)
async def tts(req: TTSRequest):
    provider = get_provider()
    voice = req.voice or TTS_VOICE
    speed = normalize_speed(req.speed or TTS_SPEED, default="+0%")
    fmt = req.format.lower()

    name = _hash_name(req.text, voice, speed, fmt)
    out_path = os.path.join(STATIC_DIR, "tts", name)
    out_url = f"/static/tts/{name}"

    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    cached = os.path.exists(out_path) and size >= MIN_VALID_BYTES
    used_provider = type(provider).__name__

    if not cached:
        try:
            result = await provider.synthesize(req.text, voice, speed, fmt)
            out_url = result.url
            size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
            if size < MIN_VALID_BYTES:
                # fallback if provider produced tiny/bad file
                raise RuntimeError("Produced tiny file; falling back to Dummy")
        except Exception:
            fallback = DummyProvider()
            result = await fallback.synthesize(req.text, voice, speed, fmt)
            out_url = result.url
            used_provider = type(fallback).__name__
            size = os.path.getsize(out_path) if os.path.exists(out_path) else 0

    return TTSResponse(
        audio_url=out_url,
        voice=voice,
        speed=speed,
        format=fmt,
        cached=cached,
        provider=used_provider,
        size=size
    )