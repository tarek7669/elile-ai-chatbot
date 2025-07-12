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
        
        # VAD Parameters
        self.SILENCE_THRESHOLD = 35  # Adjust this value based on your microphone and environment noise. 
                                      # Higher means less sensitive to quiet sounds. Lower means more sensitive.
        self.SILENCE_CHUNKS = int(self.sample_rate / self.chunk_size * 1.5) # 1.5 seconds of silence to stop
        self.MAX_RECORDING_DURATION_CHUNKS = int(self.sample_rate / self.chunk_size * 30) # Max 30 seconds to prevent infinite recording
                                                                                         # (adjust as per config.py)
        
    # def record_audio(self, duration: int = 5) -> bytes:
    #     """Record audio from microphone."""
    #     audio = pyaudio.PyAudio()
        
    #     try:
    #         stream = audio.open(
    #             format=self.audio_format,
    #             channels=self.channels,
    #             rate=self.sample_rate,
    #             input=True,
    #             frames_per_buffer=self.chunk_size
    #         )
            
    #         frames = []
    #         for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
    #             data = stream.read(self.chunk_size)
    #             frames.append(data)
            
    #         stream.stop_stream()
    #         stream.close()
            
    #         # Convert to bytes
    #         audio_data = b''.join(frames)
    #         return self._frames_to_wav_bytes(audio_data)
            
    #     finally:
    #         audio.terminate()

    def record_audio(self, duration: int = 5) -> bytes: # 'duration' parameter will now be ignored for VAD
        """Record audio from microphone with Voice Activity Detection (VAD)."""
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
            silent_chunks = 0
            speaking = False # State to track if user is currently speaking
            
            st.write("Listening for your voice...") # Provide initial feedback
            
            chunk_count = 0
            while True:
                data = stream.read(self.chunk_size)
                np_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS (Root Mean Square) energy of the chunk
                # Avoid division by zero for completely silent chunks
                mean_squared = np.mean(np_data**2) if np_data.size > 0 else 0
                rms = np.sqrt(max(0.0, mean_squared))

                # print(f"Chunk {chunk_count}: RMS = {rms:.2f}")  # Debugging output

                
                # Simple VAD logic
                if rms < self.SILENCE_THRESHOLD:
                    silent_chunks = 0
                    if not speaking:
                        speaking = True
                        st.write("🚀 Recording...") # Indicate active recording
                    frames.append(data)
                elif speaking: # If we were speaking, but now it's quiet
                    silent_chunks += 1
                    frames.append(data) # Keep recording for a bit after silence starts
                    if silent_chunks > self.SILENCE_CHUNKS:
                        st.write("✅ Detected silence, stopping recording.")
                        break # Stop recording
                else: # Not speaking yet, just silence before speech starts
                    pass # Don't append silent chunks before speech starts
                
                chunk_count += 1
                if chunk_count > self.MAX_RECORDING_DURATION_CHUNKS:
                    st.warning(f"🚫 Maximum recording duration ({self.MAX_RECORDING_DURATION_CHUNKS * self.chunk_size / self.sample_rate:.1f}s) reached.")
                    break # Stop if max duration reached
                    
            stream.stop_stream()
            stream.close()
            
            audio_data = b''.join(frames)
            
            # If no audio was recorded (e.g., user just clicked and didn't speak)
            if not audio_data:
                st.warning("No speech detected. Please try again.")
                return b'' # Return empty bytes
            
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