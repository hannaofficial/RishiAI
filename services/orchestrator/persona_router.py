from typing import List, Optional

def choose_persona(
    emotion_tags: Optional[List[str]] = None,
    last_work: Optional[str] = None,
    guidance_style: Optional[str] = None,
) -> str:
    """
    Simple rules (expand later):
    - If guidance_style == 'rational' -> 'jiddu'
    - If last_work/Gita -> 'krishna'
    - If 'breath' in guidance_style or 'anxiety' emotion -> 'patanjali'
    - Else 'omniphilosopher'
    """
    e = [x.lower() for x in (emotion_tags or [])]
    style = (guidance_style or "").lower()
    work = (last_work or "").lower()

    if style == "rational":
        return "jiddu"
    if "gita" in work or "bhagavad" in work:
        return "krishna"
    if "breath" in style or "anxiety" in e or "overthinking" in e:
        return "patanjali"
    return "omniphilosopher"
