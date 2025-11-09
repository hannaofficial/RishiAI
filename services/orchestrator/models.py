from typing import List, Optional, Literal
from pydantic import BaseModel

Lang = Literal["en"]

class Slide(BaseModel):
    image_url: str
    caption: str

class Citation(BaseModel):
    work: str
    ref: Optional[str] = None

class StoryRequest(BaseModel):
    user_id: str
    problem_text: str
    language: Lang = "en"
    sources: List[str] = ["auto"]

class StoryPayload(BaseModel):
    title: str
    slides: List[Slide]
    narration_text: str
    takeaways: List[str]
    citations: List[Citation]
    audio_url: Optional[str] = None        # (narration, if TTS done server-side)
    bg_music_url: Optional[str] = None      

class StoryResponse(BaseModel):
    story: StoryPayload
    session_id: str

class StoryQARequest(BaseModel):
    story_id: str
    question: str

class StoryQAResponse(BaseModel):
    answer_text: str
    citations: List[Citation] = []

class GuideChatRequest(BaseModel):
    session_id: str
    persona: str = "omniphilosopher"  # "krishna" | "jiddu" | ...
    message: str
    language: Lang = "en"

class GuideChatResponse(BaseModel):
    reply_text: str
    questions: List[str] = []
    citations: List[Citation] = []
    persona_selected: str



class PracticeSuggestRequest(BaseModel):
    user_id: str
    emotion_tags: List[str] = ["anxiety"]  # simple default

class PracticeItem(BaseModel):
    title: str
    why: str
    roots: str
    steps: List[str]

class PracticeSuggestResponse(BaseModel):
    practices: List[PracticeItem]
