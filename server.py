import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3"

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

class TTSRequest(BaseModel):
    text: str

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio blob using Groq Whisper API."""
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
            "temperature": 0
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            return {"text": result.get("text", "")}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Groq Whisper error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    """Generate LLM response using Groq Chat API."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=400, detail="Groq API key not configured")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are a helpful, friendly, and concise real-time voice assistant. "
        "Keep your responses natural, conversational, and direct so they sound great when read aloud."
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
    """Convert text to speech using gTTS and return audio/mpeg stream."""
    try:
        tts = gTTS(text=request.text, lang="en")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"gTTS error: {str(e)}")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
