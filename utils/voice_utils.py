"""
Lightweight STT + TTS wrappers that fit into Streamlit.
"""
import speech_recognition as sr
import pyttsx3
import streamlit as st
from utils.config_voice import VoiceConfig

cfg = VoiceConfig()

@st.cache_resource
def _get_recognizer():
    r = sr.Recognizer()
    r.pause_threshold = 0.8
    return r

@st.cache_resource
def _get_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty("rate", cfg.TTS_RATE)
    engine.setProperty("volume", cfg.TTS_VOLUME)
    voices = engine.getProperty("voices")
    for v in voices:
        if "female" in v.name.lower() or "zira" in v.name.lower():
            engine.setProperty("voice", v.id)
            break
    return engine

def listen_once() -> str | None:
    """Return transcribed text or None on failure."""
    r = _get_recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=cfg.MIC_TIMEOUT)  # <-- increased timeout
            return r.recognize_google(audio)
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None

def speak(text: str):
    """Speak text immediately (blocking)."""
    if not text.strip():
        return
    engine = _get_tts_engine()
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        # If the run loop is already started, stop and try again
        engine.stop()
        engine.say(text)
        engine.runAndWait()