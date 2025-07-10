"""Audio utilities for recording and playback."""

import pyaudio
import wave
import numpy as np
import io
import streamlit as st
from typing import Optional, Tuple
import time

class AudioRecorder:
    """Handle audio recording functionality."""
    
    def __init__(self, sample_rate: int = 22050, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        
    def record_audio(self, duration: int = 5) -> bytes:
        """Record audio from microphone."""
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Convert to bytes
            audio_data = b''.join(frames)
            return self._frames_to_wav_bytes(audio_data)
            
        finally:
            audio.terminate()
    
    def _frames_to_wav_bytes(self, frames: bytes) -> bytes:
        """Convert audio frames to WAV bytes."""
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(pyaudio.get_sample_size(self.audio_format))
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(frames)
        
        return wav_buffer.getvalue()

class AudioPlayer:
    """Handle audio playback functionality."""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
    
    def play_audio_file(self, file_path: str):
        """Play audio file."""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True
                )
                
                chunk_size = 1024
                data = wav_file.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wav_file.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            st.error(f"Error playing audio: {str(e)}")
    
    def __del__(self):
        if hasattr(self, 'audio'):
            self.audio.terminate()