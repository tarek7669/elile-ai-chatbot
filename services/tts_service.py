"""Text-to-Speech service using Coqui XTTS v2."""

import torch
from TTS.api import TTS
import logging
import tempfile
import os
from typing import Optional
from config import CONFIG
import time
import streamlit as st


from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

# Add these classes to PyTorch's safe globals list *before* loading the model
if hasattr(torch.serialization, 'add_safe_globals'): # Check for PyTorch version compatibility
    torch.serialization.add_safe_globals([
        XttsConfig,
        XttsAudioConfig,
        BaseDatasetConfig,
        XttsArgs,
    ])
else:
    # This warning indicates you might be on an older PyTorch version or a custom build
    logging.warning("PyTorch version does not support add_safe_globals. "
                    "If you encounter serialization errors, consider upgrading PyTorch.")


logger = logging.getLogger(__name__)

@st.cache_resource
def load_tts_model(model_name: str, use_gpu: bool):
    """
    Loads the TTS model only once, and caches it.
    This prevents the model from reloading on every Streamlit rerun.
    """
    try:
        # Check if CUDA is available *before* trying to load on GPU
        if use_gpu and not torch.cuda.is_available():
            st.warning("Config set to use GPU for TTS, but CUDA is not available. Falling back to CPU.")
            use_gpu = False # Force CPU if CUDA isn't detected


        device = 'cuda' if use_gpu else 'cpu'
        logger.info(f"Loading TTS model: {model_name} (GPU: {use_gpu})...")
        model = TTS(model_name=model_name).to(device)
        logger.info("TTS model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}", exc_info=True)
        st.error(f"Error loading TTS model: {e}. Please check your CUDA setup if you intended to use GPU.")
        return None

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
            # self.tts = TTS(model_name=self.model_name, gpu=True)
            
            self.tts = load_tts_model(self.model_name, use_gpu=True)

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
            # self.tts.tts_to_file(
            #     text=text,
            #     speaker_wav=self.voice_file,
            #     language="ar",
            #     file_path=output_path
            # )

            wav_output = self.tts.tts(
                text=text,
                speaker_wav=self.voice_file,
                language="ar",
            )
            
            logger.info(f"Speech synthesized successfully: {output_path}")
            # return output_path
            return wav_output
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None