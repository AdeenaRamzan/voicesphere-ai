import os
import io
import requests
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3"

# Language name (as returned by Whisper) -> gTTS voice code.
# Whisper's verbose_json response returns full language names, not ISO codes,
# so this table drives both the reply-language instruction and the TTS voice.
LANGUAGE_TO_TTS_CODE = {
    "english": "en", "spanish": "es", "french": "fr", "german": "de",
    "italian": "it", "portuguese": "pt", "dutch": "nl", "russian": "ru",
    "japanese": "ja", "korean": "ko", "chinese": "zh-CN", "arabic": "ar",
    "hindi": "hi", "urdu": "ur", "turkish": "tr", "polish": "pl",
    "vietnamese": "vi", "indonesian": "id", "thai": "th", "greek": "el",
    "swedish": "sv", "finnish": "fi", "danish": "da", "norwegian": "no",
    "ukrainian": "uk", "czech": "cs", "romanian": "ro", "hebrew": "iw",
    "bengali": "bn",
}
DEFAULT_TTS_CODE = "en"

app = FastAPI(title="Realtime AI Voice Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = None  # full language name, e.g. "spanish" (from /api/transcribe)

class TTSRequest(BaseModel):
    text: str
    lang: Optional[str] = "en"  # gTTS voice code, e.g. "es", "fr", "ur"

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: Optional[str] = Form(None)):
    """Transcribe uploaded audio using Groq Whisper. Auto-detects language unless one is forced.

    `language` (optional): ISO-639-1 code to force transcription in a specific language
    (e.g. "es"). Leave empty to let Whisper auto-detect.
    """
    if not GROQ_API_KEY:
        raise HTTPException(status_code=400, detail="Groq API key not configured")

    try:
        content = await file.read()
        filename = file.filename or "recording.webm"

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        files = {"file": (filename, content, file.content_type or "audio/webm")}
        data = {
            "model": GROQ_WHISPER_MODEL,
            "temperature": 0,
            "response_format": "verbose_json",  # returns detected language alongside text
        }
        if language:
            data["language"] = language

        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            detected_language = (result.get("language") or "english").lower()
            return {
                "text": result.get("text", ""),
                "language": detected_language,
                "tts_code": LANGUAGE_TO_TTS_CODE.get(detected_language, DEFAULT_TTS_CODE),
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Groq Whisper error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    """Generate LLM response using Groq Chat API, replying in the detected language."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=400, detail="Groq API key not configured")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    language_instruction = ""
    if request.language and request.language.lower() != "english":
        language_instruction = f" Always reply in {request.language.title()}, matching the user's language."

    system_prompt = (
        "You are a helpful, friendly, and concise real-time voice assistant. "
        "Keep your responses natural, conversational, and direct so they sound great when read aloud."
        + language_instruction
    )

    payload = {
        "model": GROQ_CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return {"response": reply}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Groq Chat error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using gTTS and return audio/mpeg stream, in the requested voice language."""
    try:
        tts = gTTS(text=request.text, lang=request.lang or "en")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"gTTS error: {str(e)}")

@app.get("/widget.js")
async def get_widget_script():
    """Serves the embeddable widget as a top-level script so client sites can do:
    <script src="https://your-domain.com/widget.js" data-agent-name="..."></script>
    """
    with open("static/widget.js", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="application/javascript")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
