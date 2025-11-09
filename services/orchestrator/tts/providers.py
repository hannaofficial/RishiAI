import os, hashlib, pathlib, asyncio
from typing import Optional

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge").lower()
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")
TTS_SPEED = os.getenv("TTS_SPEED", "+0%")
STATIC_DIR = os.getenv("STATIC_DIR", "./static")

def _hash_name(text: str, voice: str, speed: str, fmt: str = "mp3") -> str:
    h = hashlib.sha256((voice + "|" + speed + "|" + text).encode("utf-8")).hexdigest()[:24]
    return f"{h}.{fmt}"

class TTSResult:
    def __init__(self, path: str, url: str):
        self.path = path
        self.url = url

class BaseTTSProvider:
    async def synthesize(self, text: str, voice: str, speed: str, fmt: str = "mp3") -> TTSResult:
        raise NotImplementedError

class DummyProvider(BaseTTSProvider):
    async def synthesize(self, text: str, voice: str, speed: str, fmt: str = "mp3") -> TTSResult:
        # Create a 1-second silent mp3 placeholder
        out_name = _hash_name(text, voice, speed, fmt)
        out_path = os.path.join(STATIC_DIR, "tts", out_name)
        out_url = f"/static/tts/{out_name}"
        if not os.path.exists(out_path):
            # 1s silence mp3 (pre-encoded tiny file) – write once
            with open(out_path, "wb") as f:
                # Minimal header silence mp3 bytes (not pretty, but fine for placeholder)
                f.write(b"\x49\x44\x33\x03\x00\x00\x00\x00\x00\x21")  # fake ID3 header
        return TTSResult(out_path, out_url)

class EdgeTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, voice: str, speed: str, fmt: str = "mp3") -> TTSResult:
        try:
            import edge_tts
        except Exception as e:
            raise RuntimeError(f"edge-tts not available: {e}")

        out_name = _hash_name(text, voice, speed, fmt)
        out_path = os.path.join(STATIC_DIR, "tts", out_name)
        out_url  = f"/static/tts/{out_name}"

        # reuse valid cache
        if os.path.exists(out_path) and os.path.getsize(out_path) >= 4096:
            return TTSResult(out_path, out_url)

        # minimal, robust path — let edge-tts pick defaults
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=speed)
        await communicate.save(out_path)  # ⬅ no "format=" here

        # sanity: ensure file isn't tiny
        if not os.path.exists(out_path) or os.path.getsize(out_path) < 4096:
            raise RuntimeError("edge-tts wrote a tiny file")

        return TTSResult(out_path, out_url)



# def get_provider() -> BaseTTSProvider:
#     if TTS_PROVIDER == "edge":
#         return EdgeTTSProvider()
#     # Future: elif TTS_PROVIDER == "kokoro": return KokoroProvider()
#     # Future: elif TTS_PROVIDER == "piper": return PiperProvider()
#     # Future: elif TTS_PROVIDER == "coqui": return CoquiProvider()
#     # Future: elif TTS_PROVIDER == "elevenlabs": return ElevenLabsProvider()
#     return DummyProvider()




class LocalTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, voice: str, speed: str, fmt: str = "wav") -> TTSResult:
        """
        Offline TTS via pyttsx3 + espeak-ng on Linux.
        - Always writes WAV (most robust).
        - Tries best-effort voice matching (substring by name or language code).
        - Maps +N% / -N% to engine rate around its base.
        """
        import pyttsx3, time, re

        # Force WAV extension
        out_name = _hash_name(text, voice or "", speed or "", "wav").replace(".mp3", ".wav")
        out_path = os.path.join(STATIC_DIR, "tts", out_name)
        out_url  = f"/static/tts/{out_name}"

        if os.path.exists(out_path) and os.path.getsize(out_path) >= 4096:
            return TTSResult(out_path, out_url)

        engine = pyttsx3.init()
        try:
            # ----- VOICE PICK -----
            target = (voice or "").strip().lower()
            picked = False
            voices = engine.getProperty("voices") or []
            # 1) substring match against voice name/id
            for v in voices:
                name = (getattr(v, "name", "") or "").lower()
                vid  = (getattr(v, "id", "") or "").lower()
                if target and (target in name or target in vid):
                    engine.setProperty("voice", v.id)
                    picked = True
                    break
            # 2) fallback: if 'en' or 'hi' etc in target, pick first voice whose id contains that
            if not picked and target:
                m = re.search(r"[a-z]{2}", target)
                if m:
                    lang = m.group(0)
                    for v in voices:
                        vid = (getattr(v, "id", "") or "").lower()
                        if lang in vid:
                            engine.setProperty("voice", v.id)
                            picked = True
                            break
            # else leave engine default

            # ----- RATE MAPPING -----
            base_rate = engine.getProperty("rate") or 200
            rate = base_rate
            try:
                s = (speed or "+0%").strip()
                sign = +1 if s.startswith("+") else -1
                pct = int(s.replace("+","").replace("-","").replace("%",""))
                rate = max(80, min(300, int(base_rate * (1 + sign * (pct/100.0)))))
            except Exception:
                pass
            engine.setProperty("rate", rate)

            # ----- SYNTH -----
            engine.save_to_file(text, out_path)
            engine.runAndWait()
            time.sleep(0.1)  # ensure file is flushed

            if not os.path.exists(out_path) or os.path.getsize(out_path) < 4096:
                raise RuntimeError("local TTS produced tiny file")
        finally:
            try:
                engine.stop()
            except Exception:
                pass

        return TTSResult(out_path, out_url)
    
def get_provider() -> BaseTTSProvider:
    if TTS_PROVIDER == "edge":
        return EdgeTTSProvider()
    if TTS_PROVIDER == "local":
        return LocalTTSProvider()
    return DummyProvider()

