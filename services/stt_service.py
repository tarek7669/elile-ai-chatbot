"""Speech-to-Text service using OpenAI Whisper."""

import openai
import logging
from typing import Optional
import tempfile
import os
from config import CONFIG

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service using OpenAI Whisper."""
    
    def __init__(self):
        openai.api_key = CONFIG.openai_api_key
    
    def transcribe_audio(self, audio_bytes: bytes) -> Optional[str]:
        """Transcribe audio bytes to text using Whisper."""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using OpenAI Whisper
                with open(temp_file_path, 'rb') as audio_file:
                    response = openai.Audio.transcribe(
                        model=CONFIG.whisper_model,
                        file=audio_file,
                        language="ar"  # Arabic
                    )
                
                transcription = response.get('text', '').strip()
                logger.info(f"Transcription successful: {transcription[:100]}...")
                
                return transcription
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            return None