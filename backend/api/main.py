from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from backend.services.session_manager import ChatSessionManager
import os

app = FastAPI()
session_manager = ChatSessionManager()

@app.post("/chat")
async def chat(audio: UploadFile = File(...)):
    input_path = f"temp_{audio.filename}"
    with open(input_path, "wb") as f:
        f.write(await audio.read())

    result = session_manager.process_audio(input_path)

    os.remove(input_path)

    return FileResponse(result["audio_path"], media_type="audio/mpeg", filename="response.mp3")