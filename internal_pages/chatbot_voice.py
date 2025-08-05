"""
Thin wrapper that injects voice UI into the existing chatbot page.
Import this module at the top of chatbot.py and call run() once.
"""
import streamlit as st
from utils.voice_utils import listen_once, speak
from utils.conversation_manager import ConversationManager
from utils.openrouter_client import call_openrouter_api, add_to_chat_history

def _voice_controls(conv_manager: ConversationManager):
    """Render mic button + TTS checkbox inside the chat column."""
    col_mic, col_tts = st.columns([1, 2])
    with col_mic:
        if st.button("🎤 Speak", key="mic_btn", help="Click and talk"):
            with st.spinner("🎙️ Listening…"):
                text = listen_once()
            if text:
                add_to_chat_history("user", text)
                conv_manager.add_user_message(text)
                with st.spinner("🤔 Thinking…"):
                    response = call_openrouter_api(
                        text,
                        conversation_history=st.session_state.get("chat_history", []),
                        conversation_state=conv_manager.get_conversation_state()
                    )
                add_to_chat_history("assistant", response)
                conv_manager.add_assistant_message(response)
                if st.session_state.get("voice_reply", True):
                    speak(response)
                st.rerun()
            else:
                st.error("❓ Could not understand audio")
    with col_tts:
        st.checkbox(
            "🔊 Read responses aloud",
            value=True,
            key="voice_reply",
            help="Uncheck to silence automatic TTS replies",
        )

def run():
    """
    Call this once inside chatbot_page() **before** the normal text input form.
    It adds the voice UI and returns immediately.
    """
    if "conv_manager" not in st.session_state:
        st.session_state.conv_manager = ConversationManager()
    _voice_controls(st.session_state.conv_manager)