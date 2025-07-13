"""Configuration settings for the Omani AI Therapist system."""

import os
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for AI models and services."""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    whisper_model: str = "whisper-1"  # OpenAI Whisper API
    gpt_model: str = "gpt-4o"
    
    # Anthropic Configuration
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    # claude_model: str = "claude-3-opus-20240229"
    claude_model: str = "claude-opus-4-20250514"
    
    # Audio Configuration
    sample_rate: int = 22050
    audio_format: str = "wav"
    max_recording_duration: int = 30  # seconds
    
    # Performance Configuration
    max_response_time: int = 20  # seconds
    chunk_size: int = 1024
    
    # Emotion Model Configuration
    emotion_model_name: str = "CAMeL-Lab/bert-base-arabic-camelbert-mix-sentiment"
    emotion_threshold: float = 0.7
    
    # TTS Configuration
    tts_model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    voice_file_path: str = "data/voices/audio.wav"
    
    # Therapeutic Configuration
    crisis_keywords: list = None
    
    def __post_init__(self):
        if self.crisis_keywords is None:
            self.crisis_keywords = [
                "انتحار", "موت", "قتل نفسي", "لا أريد العيش", 
                "أريد أن أموت", "suicide", "kill myself", "want to die"
            ]

# Global configuration instance
CONFIG = ModelConfig()

# Validation
def validate_config():
    """Validate that required configuration is present."""
    if not CONFIG.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if not CONFIG.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")