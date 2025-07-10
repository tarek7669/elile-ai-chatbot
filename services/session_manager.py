"""Session manager for the complete STT -> Emotion -> GPT -> TTS pipeline."""

import time
import logging
from typing import Optional, Dict, Any
from services.stt_service import STTService
from services.emotion_service import EmotionService
from services.gpt_service import GPTService
from services.tts_service import TTSService
from utils.text_utils import normalize_arabic_text

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages the complete therapy session pipeline."""
    
    def __init__(self):
        self.stt_service = STTService()
        self.emotion_service = EmotionService()
        self.gpt_service = GPTService()
        self.tts_service = TTSService()
    
    def process_voice_input(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Process complete voice input through the pipeline."""
        
        start_time = time.time()
        result = {
            "success": False,
            "transcription": None,
            "emotions": None,
            "response_text": None,
            "audio_file": None,
            "processing_time": 0,
            "error": None
        }
        
        try:
            # Step 1: Speech to Text
            logger.info("Starting transcription...")
            transcription = self.stt_service.transcribe_audio(audio_bytes)
            
            if not transcription:
                result["error"] = "Failed to transcribe audio"
                return result
            
            result["transcription"] = transcription
            logger.info(f"Transcription completed: {transcription[:50]}...")
            
            # Step 2: Emotion Detection
            logger.info("Detecting emotions...")
            normalized_text = normalize_arabic_text(transcription)
            emotions = self.emotion_service.detect_emotion(normalized_text)
            result["emotions"] = emotions
            
            primary_emotion = max(emotions, key=emotions.get)
            logger.info(f"Primary emotion detected: {primary_emotion}")
            
            # Step 3: Generate Therapeutic Response
            logger.info("Generating therapeutic response...")
            response_text = self.gpt_service.generate_therapeutic_response(
                transcription, emotions
            )
            
            if not response_text:
                result["error"] = "Failed to generate response"
                return result
            
            result["response_text"] = response_text
            logger.info(f"Response generated: {response_text[:50]}...")
            
            # Step 4: Text to Speech
            logger.info("Synthesizing speech...")
            audio_file = self.tts_service.synthesize_speech(response_text)
            
            if not audio_file:
                result["error"] = "Failed to synthesize speech"
                return result
            
            result["audio_file"] = audio_file
            result["success"] = True
            
            # Calculate processing time
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            
            logger.info(f"Pipeline completed successfully in {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in pipeline: {str(e)}")
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result