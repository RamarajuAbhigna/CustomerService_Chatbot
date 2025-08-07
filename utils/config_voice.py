"""
Separate voice settings so the main config.py stays untouched.
"""
import os
from dotenv import load_dotenv
load_dotenv()

class VoiceConfig:
    TTS_RATE   = int(os.getenv("TTS_RATE", 180))          # words / min
    TTS_VOLUME = float(os.getenv("TTS_VOLUME", 0.9))
    MIC_TIMEOUT = int(os.getenv("MIC_TIMEOUT", 9))