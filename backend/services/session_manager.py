from .stt_service import STTService
from .openai_service import GPTService
from .tts_service import TTSService
from .claude_service import ClaudeService
from .emotion_handler import EmotionDetector

class ChatSessionManager:
    def __init__(self):
        self.stt = STTService()
        self.gpt = GPTService()
        self.tts = TTSService()
        self.claude = ClaudeService()
        self.emotion = EmotionDetector()

    def process_audio(self, audio_path: str) -> dict:
        transcription = self.stt.transcribe(audio_path)
        emotion_info = self.emotion.detect(transcription)
        gpt_reply = self.gpt.generate_response(transcription)
        claude_validation = self.claude.validate_response(gpt_reply)
        audio_output_path = self.tts.synthesize(gpt_reply)

        return {
            "transcription": transcription,
            "emotion": emotion_info,
            "gpt_reply": gpt_reply,
            "claude_validation": claude_validation,
            "audio_path": audio_output_path
        }