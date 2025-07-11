"""Streamlit frontend for the Omani AI Therapist."""

import streamlit as st
import time
import os
from services.session_manager import SessionManager
from utils.audio_utils import AudioRecorder, AudioPlayer
from utils.logging_config import setup_logging
from config import CONFIG, validate_config

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="المعالج النفسي العماني - Omani AI Therapist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
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
        "processing": "status-processing"
    }
    
    status_messages = {
        "ready": "🎤 جاهز للاستماع - Ready to Listen",
        "listening": "👂 أستمع إليك - Listening...",
        "processing": "🤔 أفكر في إجابتك - Processing your response..."
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

def display_response(response_text: str, transcription: str = ""):
    """Display the AI response."""
    st.markdown("### الرد - Response")
    
    if transcription:
        st.markdown(f"""
        <div class="response-box">
            <h4>ما قلته - What you said:</h4>
            <p class="arabic-text">{transcription}</p>
            <hr>
            <h4>ردي - My response:</h4>
            <p class="arabic-text">{response_text}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="response-box">
            <p class="arabic-text">{response_text}</p>
        </div>
        """, unsafe_allow_html=True)

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
        
        # Settings
        st.markdown("## الإعدادات - Settings")
        
        recording_duration = st.slider(
            "مدة التسجيل (ثانية) - Recording Duration (seconds)",
            min_value=3,
            max_value=30,
            value=5
        )
        
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
        
        return recording_duration

def display_conversation_history():
    """Display conversation history."""
    if st.session_state.conversation_history:
        st.markdown("## تاريخ المحادثة - Conversation History")
        
        for i, entry in enumerate(reversed(st.session_state.conversation_history[-5:])):
            with st.expander(f"محادثة {len(st.session_state.conversation_history) - i}"):
                st.markdown(f"**المستخدم:** {entry['user']}")
                st.markdown(f"**المعالج:** {entry['therapist']}")
                if entry.get('emotions'):
                    st.markdown(f"**المشاعر:** {entry['emotions']}")

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
        recording_duration = display_sidebar()
        
        # Display current status
        display_status(st.session_state.current_status)
        
        # Main interaction area
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Record button
            if st.button("🎤 ابدأ التسجيل - Start Recording", 
                        key="record_btn",
                        help="اضغط لبدء تسجيل صوتك",
                        use_container_width=True):
                
                st.session_state.current_status = "listening"
                st.rerun()
            
            # Processing area
            if st.session_state.current_status == "listening":
                with st.spinner("جاري التسجيل... Recording..."):
                    try:
                        # Record audio
                        audio_bytes = st.session_state.audio_recorder.record_audio(recording_duration)
                        
                        # Save to session so it's available after rerun
                        st.session_state.audio_bytes = audio_bytes
                        st.session_state.current_status = "processing"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"خطأ في التسجيل - Recording error: {str(e)}")
                        st.session_state.current_status = "ready"
                        st.rerun()
            
            elif st.session_state.current_status == "processing":
                with st.spinner("جاري المعالجة... Processing..."):
                    try:
                        # Process through pipeline
                        result = st.session_state.session_manager.process_voice_input(st.session_state.audio_bytes)
                        
                        if result["success"]:
                            # Display results
                            display_emotions(result["emotions"])
                            display_response(result["response_text"], result["transcription"])
                            
                            # Play audio response
                            if result["audio_file"] and os.path.exists(result["audio_file"]):
                                st.audio(result["audio_file"], format="audio/wav")
                                
                                # Auto-play using HTML audio element
                                st.markdown(f"""
                                <audio autoplay>
                                    <source src="data:audio/wav;base64,{result['audio_file']}" type="audio/wav">
                                </audio>
                                """, unsafe_allow_html=True)
                            
                            # Update conversation history
                            st.session_state.conversation_history.append({
                                "user": result["transcription"],
                                "therapist": result["response_text"],
                                "emotions": result["emotions"],
                                "timestamp": time.time()
                            })
                            
                            # Update processing time
                            st.session_state.processing_time = result["processing_time"]
                            
                            # Check if response was within time limit
                            if result["processing_time"] > CONFIG.max_response_time:
                                st.warning(f"⚠️ الرد استغرق {result['processing_time']:.1f} ثانية (أكثر من الحد المطلوب)")
                            
                        else:
                            st.error(f"فشل في المعالجة - Processing failed: {result.get('error', 'Unknown error')}")
                        
                        st.session_state.current_status = "ready"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"خطأ في المعالجة - Processing error: {str(e)}")
                        st.session_state.current_status = "ready"
                        st.rerun()
        
        # Display conversation history
        display_conversation_history()
        
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