from gtts import gTTS
import uuid

class TTSService:
    def __init__(self, lang='ar'):
        self.lang = lang

    def synthesize(self, text: str) -> str:
        filename = f"output_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text, lang=self.lang)
        tts.save(filename)
        return filename