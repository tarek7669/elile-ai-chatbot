"""Text-to-Speech service using Coqui XTTS v2."""

import torch
from TTS.api import TTS
import logging
import tempfile
import os
from typing import Optional
from config import CONFIG
import time

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using Coqui XTTS v2."""
    
    def __init__(self):
        self.model_name = CONFIG.tts_model_name
        self.voice_file = CONFIG.voice_file_path
        self.tts = None
        self._load_model()
    
    def _load_model(self):
        """Load TTS model."""
        try:
            self.tts = TTS(model_name=self.model_name)
            logger.info(f"TTS model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading TTS model: {str(e)}")
            self.tts = None
    
    def synthesize_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Synthesize speech from text."""
        
        if not self.tts:
            logger.error("TTS model not available")
            return None
        
        if not text:
            logger.error("No text provided for synthesis")
            return None
        
        try:
            # Create output path if not provided
            if not output_path:
                output_path = f"outputs/response_{int(time.time())}.wav"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if voice file exists
            if not os.path.exists(self.voice_file):
                logger.error(f"Voice file not found: {self.voice_file}")
                return None
            
            # Synthesize speech
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.voice_file,
                language="ar",
                file_path=output_path
            )
            
            logger.info(f"Speech synthesized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None