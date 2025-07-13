"""
Setup and run script for the Omani AI Therapist application.
"""

import subprocess
import sys
import os
import logging

def setup_logging():
    """Setup logging for the installer."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def install_requirements():
    """Install required packages with proper dependency resolution."""
    logger = setup_logging()
    
    try:
        # Check Python version
        if sys.version_info < (3, 10):
            logger.error("Python 3.10+ required. Current version: {}.{}.{}".format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro
            ))
            sys.exit(1)
        
        logger.info(f"Installing packages for Python {sys.version_info.major}.{sys.version_info.minor}...")
        
        # Upgrade pip first
        logger.info("Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install in stages to avoid conflicts
        logger.info("Stage 1: Installing core ML dependencies...")
        core_ml_packages = [
            "numpy",
            "scipy==1.11.2", 
            "torch==2.7.1+cu128",
            "torchvision==0.22.1+cu128",
            "torchaudio==2.7.1+cu128"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + core_ml_packages)
        
        logger.info("Stage 2: Installing ML frameworks...")
        ml_packages = [
            "transformers==4.33.0",
            "librosa",
            "soundfile==0.12.1",
            "TTS==0.22.0",
            "sounddevice"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + ml_packages)
        
        logger.info("Stage 3: Installing APIs and web framework...")
        api_packages = [
            "openai==0.28.1",
            "anthropic==0.8.0",
            "streamlit==1.28.1"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + api_packages)
        
        logger.info("Stage 4: Installing audio and remaining dependencies...")
        remaining_packages = [
            "PyAudio",
            "python-dotenv==1.0.0",
            "pandas",
            "pillow==10.0.0"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + remaining_packages)
        
        logger.info("All packages installed successfully!")
        
        # Verify critical imports
        logger.info("Verifying installations...")
        critical_imports = {
            "streamlit": "streamlit",
            "openai": "openai", 
            "anthropic": "anthropic",
            "torch": "torch",
            "transformers": "transformers",
            "TTS": "TTS",
            "pyaudio": "pyaudio",
            "librosa": "librosa",
            "soundfile": "soundfile",
            "numpy": "numpy",
            "scipy": "scipy"
        }
        
        failed_imports = []
        for package, import_name in critical_imports.items():
            try:
                __import__(import_name)
                logger.info(f"✓ {package}")
            except ImportError as e:
                logger.error(f"✗ {package}: {e}")
                failed_imports.append(package)
        
        if failed_imports:
            logger.error(f"Failed to import: {', '.join(failed_imports)}")
            logger.error("Please check system dependencies and try manual installation")
            return False
        
        logger.info("All critical packages verified successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install packages: {e}")
        logger.error("Try installing manually with staged approach:")
        logger.error("1. pip install numpy==1.24.3 scipy==1.11.1")
        logger.error("2. pip install torch==2.0.1 torchaudio==2.0.2")
        logger.error("3. pip install transformers==4.30.2 TTS==0.13.3")
        logger.error("4. pip install streamlit==1.28.1 openai==0.28.1")
        return False

def create_directories():
    """Create necessary directories."""
    logger = setup_logging()
    
    directories = [
        "data/voices",
        "outputs",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def check_environment():
    """Check environment variables."""
    logger = setup_logging()
    
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these environment variables before running the application.")
        sys.exit(1)
    
    logger.info("Environment variables check passed!")

def create_sample_voice_file():
    """Create a sample voice file if it doesn't exist."""
    logger = setup_logging()
    
    voice_file_path = "data/voices/audio.wav"
    
    if not os.path.exists(voice_file_path):
        logger.warning(f"Voice file not found: {voice_file_path}")
        logger.warning("Please place an Omani voice sample (3-10 seconds, 22050Hz) at this location.")
        logger.warning("For now, creating a placeholder file.")
        
        # Create placeholder file
        with open(voice_file_path, 'w') as f:
            f.write("# Placeholder for Omani voice sample\n")
            f.write("# Please replace with actual WAV file\n")

def run_application():
    """Run the Streamlit application."""
    logger = setup_logging()
    
    try:
        logger.info("Starting Omani AI Therapist application...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.error(f"Failed to run application: {e}")
        sys.exit(1)

def main():
    """Main setup and run function."""
    logger = setup_logging()
    
    logger.info("🧠 Omani AI Therapist - Setup and Run")
    logger.info("=" * 50)
    
    # Setup steps
    logger.info("Step 1: Checking environment...")
    check_environment()
    
    logger.info("Step 2: Creating directories...")
    create_directories()
    
    logger.info("Step 3: Installing requirements...")
    install_requirements()
    
    logger.info("Step 4: Checking voice file...")
    create_sample_voice_file()
    
    logger.info("Step 5: Starting application...")
    run_application()

if __name__ == "__main__":
    main()