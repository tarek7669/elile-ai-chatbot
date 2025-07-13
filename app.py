"""Streamlit frontend for the Omani AI Therapist."""

import numpy as np
import streamlit as st
import time
import os
from services.session_manager import SessionManager
from utils.audio_utils import AudioRecorder, AudioPlayer
from utils.logging_config import setup_logging
from config import CONFIG, validate_config
import sounddevice as sd

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="المعالج النفسي العماني - Omani AI Therapist",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #2E8B57;
    font-size: 2.5em;
    margin-bottom: 30px;
    font-weight: bold;
}

.status-box {
    color: #031a2e;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    text-align: center;
}

.status-listening {
    border: 2px solid #4CAF50;
}

.status-processing {
    border: 2px solid #FF9800;
}

.status-ready {
    border: 2px solid #2196F3;
}

.response-box {
    background-color: #F5F5F5;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    border-left: 5px solid #2E8B57;
}

.emotion-indicator {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 20px;
    margin: 5px;
    font-weight: bold;
}

.emotion-positive {
    background-color: #4CAF50;
    color: white;
}

.emotion-negative {
    background-color: #F44336;
    color: white;
}

.emotion-neutral {
    background-color: #9E9E9E;
    color: white;
}

.sidebar-info {
    background-color: #031a2e;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

.arabic-text {
    font-family: 'Tahoma', 'Arial Unicode MS', sans-serif;
    font-size: 1.2em;
    line-height: 1.6;
    direction: rtl;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    
    if 'audio_recorder' not in st.session_state:
        st.session_state.audio_recorder = AudioRecorder()
    
    if 'audio_player' not in st.session_state:
        st.session_state.audio_player = AudioPlayer()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_status' not in st.session_state:
        st.session_state.current_status = "ready"
    
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0

    if 'stop_signal' not in st.session_state:
        st.session_state.stop_signal = False

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        🧠 المعالج النفسي العماني<br>
        <small>Omani AI Therapist</small>
    </div>
    """, unsafe_allow_html=True)

def display_status(status: str, message: str = ""):
    """Display current status."""
    status_classes = {
        "ready": "status-ready",
        "listening": "status-listening",
        "processing": "status-processing",
        "speaking": "status-speaking"
    }
    
    status_messages = {
        "ready": "🎤 جاهز للاستماع - Ready to Listen",
        "listening": "👂 أستمع إليك - Listening...",
        "processing": "🤔 أفكر في إجابتك - Processing your response...",
        "speaking": "🔊 أجيبك الآن - Speaking..."
    }
    
    display_message = message or status_messages.get(status, "")
    css_class = status_classes.get(status, "status-ready")
    
    st.markdown(f"""
    <div class="status-box {css_class}">
        <h3>{display_message}</h3>
    </div>
    """, unsafe_allow_html=True)

def display_emotions(emotions: dict):
    """Display emotion indicators."""
    if not emotions:
        return
    
    st.markdown("### المشاعر المكتشفة - Detected Emotions")
    
    emotion_html = ""
    for emotion, confidence in emotions.items():
        if confidence > 0.1:  # Only show emotions with significant confidence
            emotion_class = f"emotion-{emotion}"
            emotion_html += f"""
            <span class="{emotion_class} emotion-indicator">
                {emotion}: {confidence:.1%}
            </span>
            """
    
    if emotion_html:
        st.markdown(emotion_html, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with app information and controls."""
    with st.sidebar:
        st.markdown("## معلومات التطبيق - App Info")
        
        st.markdown("""
        <div class="sidebar-info">
            <h3>🎯 الهدف - Purpose</h3>
            <p>مساعد نفسي ذكي يتحدث باللهجة العمانية</p>
            <p>AI therapist speaking in Omani dialect</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-info">
            <h3>🔧 التقنيات - Technologies</h3>
            <ul>
                <li>🎤 OpenAI Whisper (STT)</li>
                <li>🧠 GPT-4 + Claude Opus</li>
                <li>💭 Arabic Emotion Detection</li>
                <li>🔊 Coqui XTTS v2 (TTS)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-info">
            <h3>📞 طوارئ - Emergency</h3>
            <p><strong>خط المساعدة النفسية:</strong><br>
            🆘 16262</p>
            <p><strong>Mental Health Helpline:</strong><br>
            🆘 16262</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.processing_time > 0:
            st.markdown(f"""
            <div class="sidebar-info">
                <h3>⏱️ وقت المعالجة - Processing Time</h3>
                <p><strong>{st.session_state.processing_time:.2f} seconds</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        show_debug = st.checkbox("إظهار تفاصيل تقنية - Show Debug Info")
        
        if show_debug:
            st.markdown("### Debug Information")
            st.json({
                "OpenAI API": bool(CONFIG.openai_api_key),
                "Anthropic API": bool(CONFIG.anthropic_api_key),
                "Voice File": os.path.exists(CONFIG.voice_file_path),
                "Max Response Time": CONFIG.max_response_time,
                "Sample Rate": CONFIG.sample_rate
            })

def stop_talking():
    """Stops current recording/playback and resets state."""
    logger.info("Stop button clicked. Setting stop_signal.")
    st.session_state.stop_signal = True # Signal to stop
    
    # Try to stop sounddevice playback immediately
    try:
        if sd.get_stream().active: # Check if a sounddevice stream is active
            sd.stop()
            sd.wait() # Wait briefly for it to finish stopping
            logger.info("sounddevice playback stopped.")
    except sd.PortAudioError as e:
        logger.warning(f"Could not stop sounddevice stream (might not be active): {e}")
    except Exception as e:
        logger.error(f"Unexpected error when trying to stop sounddevice: {e}")

    # Reset statuses
    st.session_state.current_status = "ready"
    st.session_state.audio_bytes = None # Clear any pending audio
    # The record_audio function itself needs to check st.session_state.stop_signal
    # and exit gracefully if it's set. This requires a change in audio_utils.py as well.
    st.rerun() # Rerun to update the UI and stop any loops


def main():
    """Main application function."""
    try:
        # Validate configuration
        validate_config()
        
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Display sidebar and get settings
        display_sidebar()
        
        # Create a container for the chat messages
        chat_container = st.container()

        # Display conversation history in the chat container first
        with chat_container:
            for entry in st.session_state.conversation_history:
                with st.chat_message("user"):
                    st.markdown(f'<p class="arabic-text">{entry["user"]}</p>', unsafe_allow_html=True)
                with st.chat_message("assistant"):
                    st.markdown(f'<p class="arabic-text">{entry["therapist"]}</p>', unsafe_allow_html=True)
                    if entry.get('emotions'):
                        # Optionally display emotions here, or in debug only
                        pass # display_emotions(entry['emotions'])
        
        # Display current status
        display_status(st.session_state.current_status)
        
        # Main interaction area
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            button_label = "🎤 ابدأ المحادثة - Start talking"
            button_key = "record_btn"
            button_help = "اضغط لبدء الكلام"
            is_button_disabled = False

            if st.session_state.current_status != "ready":
                button_label = "🚫 إيقاف - Stop"
                button_key = "stop_btn" # Use a different key to avoid conflicts
                button_help = "اضغط لإيقاف التسجيل أو المعالجة أو التحدث"

            # Create the button
            if st.button(button_label, 
                         key=button_key,
                         help=button_help,
                         use_container_width=True,
                         on_click=stop_talking if st.session_state.current_status != "ready" else None): # Call stop_talking if not ready
                
                # If current_status is "ready", it means "Start talking" was clicked
                if st.session_state.current_status == "ready":
                    st.session_state.stop_signal = False # Ensure stop signal is false when starting
                    st.session_state.current_status = "listening"
                    st.rerun()
            
            # Processing area
            if st.session_state.current_status == "listening":
                with st.spinner("جاري التسجيل... Recording..."):
                    try:
                        # Record audio
                        audio_bytes = st.session_state.audio_recorder.record_audio()

                        if st.session_state.stop_signal:
                            logger.info("Recording stopped by user.")
                            st.session_state.stop_signal = False # Reset signal
                            st.session_state.current_status = "ready"
                            st.rerun()
                        elif audio_bytes: 
                            st.session_state.audio_bytes = audio_bytes
                            st.session_state.current_status = "processing"
                            st.rerun()
                        else: # No speech detected
                            st.warning("لم يتم الكشف عن كلام. يرجى المحاولة مرة أخرى. - No speech detected. Please try again.")
                            st.session_state.current_status = "ready"
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"خطأ في التسجيل - Recording error: {str(e)}")
                        st.session_state.current_status = "ready"
                        st.rerun()
            
            elif st.session_state.current_status == "processing":
                # Display user's transcription immediately after recording
                # This ensures the user's input appears quickly
                if 'user_message_placeholder' not in st.session_state:
                    st.session_state.user_message_placeholder = None

                if st.session_state.user_message_placeholder is None and st.session_state.audio_bytes:
                    with chat_container:
                        with st.chat_message("user"):
                            # Create an empty placeholder to update later with actual transcription
                            st.session_state.user_message_placeholder = st.empty()
                            st.session_state.user_message_placeholder.markdown(f'<p class="arabic-text">...</p>', unsafe_allow_html=True)
                with st.spinner("جاري المعالجة... Processing..."):
                    if st.session_state.stop_signal:
                        logger.info("Processing skipped due to stop signal.")
                        st.session_state.stop_signal = False # Reset signal
                        st.session_state.current_status = "ready"
                        st.rerun()
                        return # Exit the function to prevent further processing
                    try:
                        # Process through pipeline
                        result = st.session_state.session_manager.process_voice_input(st.session_state.audio_bytes, st.session_state.conversation_history)

                        st.session_state.audio_bytes = None  # Clear audio bytes after processing
                        
                        if result["success"]:
                            # --- MODIFIED: Update the user's displayed transcription placeholder ---
                            if st.session_state.user_message_placeholder:
                                st.session_state.user_message_placeholder.markdown(
                                    f'<p class="arabic-text">{result["transcription"]}</p>', 
                                    unsafe_allow_html=True
                                )
                                # Clear the placeholder reference so a new one is created next turn
                                st.session_state.user_message_placeholder = None 

                            # --- ADDED: Display therapist's response in real-time within the chat_container ---
                            with chat_container:
                                with st.chat_message("assistant"):
                                    st.markdown(f'<p class="arabic-text">{result["response_text"]}</p>', unsafe_allow_html=True)
                                    if result.get('emotions'):
                                        display_emotions(result['emotions']) # Display emotions below AI response
                            
                            # Update conversation history
                            st.session_state.conversation_history.append({
                                "user": result["transcription"],
                                "therapist": result["response_text"],
                                "emotions": result["emotions"],
                                "timestamp": time.time()
                            })
                            
                            # Play audio response
                            if result["audio_file"]:
                                st.session_state.audio_bytes = result["audio_file"]
                                st.session_state.current_status = "speaking"
                                st.rerun()
                            else: # If no audio file returned
                                st.session_state.current_status = "ready"
                                st.rerun()
                            
                            # Update processing time
                            st.session_state.processing_time = result["processing_time"]
                            
                            # Check if response was within time limit
                            if result["processing_time"] > CONFIG.max_response_time:
                                st.warning(f"⚠️ الرد استغرق {result['processing_time']:.1f} ثانية (أكثر من الحد المطلوب)")

                            
                            # sd.wait()  # Wait until playback is done
                            
                        else:
                            st.error(f"فشل في المعالجة - Processing failed: {result.get('error', 'Unknown error')}")
                        
                        st.session_state.current_status = "listening"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"خطأ في المعالجة - Processing error: {str(e)}")
                        st.session_state.current_status = "ready"
                        st.rerun()
            elif st.session_state.current_status == "speaking":
                with st.spinner("جاري التحدث... Speaking..."):
                    try:
                        # Play the audio response
                        if 'audio_bytes' in st.session_state:
                            audio_bytes = st.session_state.audio_bytes
                            sd.play(np.array(audio_bytes), samplerate=CONFIG.sample_rate)
                            sd.wait()  # Wait until playback is done
                        
                        st.session_state.current_status = "listening"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"خطأ في التحدث - Speaking error: {str(e)}")
                        st.session_state.current_status = "ready"
                        st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p>🤖 المعالج النفسي العماني - Omani AI Therapist</p>
            <p>تم التطوير بأحدث تقنيات الذكاء الاصطناعي - Powered by Advanced AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"خطأ في التطبيق - Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()