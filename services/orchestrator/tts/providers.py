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
        out_url = f"/static/tts/{out_name}"

        if os.path.exists(out_path) and os.path.getsize(out_path) > 128:
            return TTSResult(out_path, out_url)

        communicate = edge_tts.Communicate(text, voice=voice, rate=speed)
        with open(out_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        return TTSResult(out_path, out_url)

def get_provider() -> BaseTTSProvider:
    if TTS_PROVIDER == "edge":
        return EdgeTTSProvider()
    # Future: elif TTS_PROVIDER == "kokoro": return KokoroProvider()
    # Future: elif TTS_PROVIDER == "piper": return PiperProvider()
    # Future: elif TTS_PROVIDER == "coqui": return CoquiProvider()
    # Future: elif TTS_PROVIDER == "elevenlabs": return ElevenLabsProvider()
    return DummyProvider()
