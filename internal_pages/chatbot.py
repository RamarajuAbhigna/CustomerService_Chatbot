"""AI Chatbot page for customer service."""

import streamlit as st
import json
from datetime import datetime
from utils.openrouter_client import (
    call_openrouter_api, add_to_chat_history, clear_chat_history
)
from utils.conversation_manager import ConversationManager
from utils.database import db_manager
from internal_pages.chatbot_voice import run as _inject_voice

def chatbot_page():
    """AI-powered customer service chatbot page."""
    _inject_voice()   # <-- NEW: add voice controls
    # Check if we should show chat history page
    if st.session_state.get('show_chat_history', False):
        _show_chat_history_page()
        return

    # Initialize conversation manager
    if 'conv_manager' not in st.session_state:
        st.session_state.conv_manager = ConversationManager()
    conv_manager = st.session_state.conv_manager

    # Page header (replaced Pikachu header with simple header)
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Customer Service Assistant</h1>
        <p>Get instant help with your orders, billing, and account questions</p>
    </div>
    """, unsafe_allow_html=True)

    # Main layout: chat and actions
    

    # Create two columns - chat area and quick actions
    col_chat, col_actions = st.columns([3, 1])

    with col_chat:
    #     # Chat container
    #     st.markdown("""
    #     <div style="
    #         background: white;
    #         border-radius: 15px;
    #         padding: 1.5rem;
    #         box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    #         margin-bottom: 1rem;
    #         min-height: 500px;
    #         max-height: 600px;
    #         overflow-y: auto;
    #     ">
    #     """, unsafe_allow_html=True)

        # Display chat history
        chat_history = st.session_state.get('chat_history', [])
        
        if not chat_history:
            # Welcome message
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
                border-left: 4px solid #28a745;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                color: #155724;
            ">
                <h4 style="margin: 0 0 0.5rem 0;">👋 Welcome to QuickDeliver Support!</h4>
                <p style="margin: 0;">I'm your AI assistant, ready to help with:</p>
                <ul style="margin: 0.5rem 0 0 1rem;">
                    <li>Order tracking and delivery updates</li>
                    <li>Billing questions and refund requests</li>
                    <li>Restaurant recommendations</li>
                    <li>Account settings and subscription management</li>
                </ul>
                <p style="margin: 0.5rem 0 0 0;"><strong>How can I assist you today?</strong></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display conversation
            for message in chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        padding: 1rem;
                        border-radius: 15px 15px 5px 15px;
                        margin: 0.5rem 0 0.5rem 2rem;
                        border-left: 3px solid #2196f3;
                        color: #1565c0;
                        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">👤</span>
                            <strong>You</strong>
                        </div>
                        <div style="line-height: 1.5;">{message['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                        padding: 1rem;
                        border-radius: 15px 15px 15px 5px;
                        margin: 0.5rem 2rem 0.5rem 0;
                        border-left: 3px solid #9c27b0;
                        color: #6a1b9a;
                        box-shadow: 0 2px 8px rgba(156, 39, 176, 0.2);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">🤖</span>
                            <strong>AI Assistant</strong>
                        </div>
                        <div style="line-height: 1.5;">{message['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Chat input form
        # Create columns to reduce input width
        col_left, col_input, col_right = st.columns([0.1, 5.6, 0.1])

        
        with col_input:
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Type your message here...",
                    placeholder="Ask me anything about your orders, billing, or account...",
                    key="chat_input",
                    label_visibility="collapsed"
                )
                submit_button = st.form_submit_button("💬 Send", use_container_width=True)
                st.markdown("<style>div.stButton > button { margin-left: 0 !important; display: block !important; }</style>", unsafe_allow_html=True)

                if submit_button and user_input.strip():
                    # Add user message to history and conversation manager
                    add_to_chat_history("user", user_input)
                    conv_manager.add_user_message(user_input)

                    # Get AI response with conversation context
                    with st.spinner("🤔 Thinking..."):
                        # Get updated chat history after adding user message
                        updated_chat_history = st.session_state.get('chat_history', [])
                        response = call_openrouter_api(
                            user_input, 
                            conversation_history=updated_chat_history,
                            conversation_state=conv_manager.get_conversation_state()
                        )

                    # Add AI response to history and update conversation state
                    add_to_chat_history("assistant", response)
                    conv_manager.add_assistant_message(response)

                    # Rerun to show new messages and clear form
                    st.rerun()

    with col_actions:
        # Quick Actions Section
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4 style="color: #e65100; margin-bottom: 1rem;">⚡ Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📦 Track Order", key="track_order_btn", use_container_width=True):
            _handle_quick_action("I want to track my recent order", conv_manager)

        if st.button("💰 Billing Help", key="billing_help_btn", use_container_width=True):
            _handle_quick_action("I have a question about my bill", conv_manager)

        if st.button("🍕 Restaurant Recs", key="restaurant_recs_btn", use_container_width=True):
            _handle_quick_action("Can you recommend some restaurants?", conv_manager)

        if st.button("⚙️ Account Settings", key="account_settings_btn", use_container_width=True):
            _handle_quick_action("Help me with my account settings", conv_manager)

        if st.button("💸 Request Refund", key="refund_btn", use_container_width=True):
            _handle_quick_action("I would like to request a refund for my recent order", conv_manager)

        # Chat History Management
        st.markdown("---")
        if st.button("📚 Chat History", key="chat_history_btn", use_container_width=True):
            st.session_state.show_chat_history = True
            st.rerun()

        if st.button("💾 Save Chat", key="save_chat_btn", use_container_width=True):
            username = st.session_state.get('username', '')
            chat_history = st.session_state.get('chat_history', [])
            
            print(f"Save button clicked - Username: {username}, Chat length: {len(chat_history)}")
            
            if username and chat_history:
                with st.spinner("Saving chat..."):
                    success = db_manager.save_chat_history(username, chat_history)
                    print(f"Save result: {success}")
                    
                if success:
                    st.success("✅ Chat saved successfully!")
                else:
                    st.error("❌ Failed to save chat history")
            elif not username:
                st.error("❌ No user logged in")
            else:
                st.warning("⚠️ No chat messages to save")

        if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
            clear_chat_history()
            conv_manager.reset_conversation()
            st.rerun()

        # Conversation Status
        current_topic = conv_manager.get_current_topic()
        if current_topic:
            st.markdown("---")
            st.markdown(f"**Current Topic:** {current_topic}")
            st.markdown(f"**Messages in topic:** {conv_manager.get_topic_message_count()}")

        # Chat Tips in expandable section
        with st.expander("💡 Chat Tips"):
            st.markdown("""
            **What I can help you with:**
            - 📦 Track your orders and delivery status
            - 💰 Answer billing and payment questions
            - 🍕 Recommend restaurants based on your preferences
            - ⚙️ Help with account settings and subscription
            - 💸 Process refund requests step-by-step
            - 🎯 Find deals and special offers
            - 📞 General customer support
            
            **Tips for better responses:**
            - Be specific about your issue
            - Mention order IDs if you have them
            - Follow the conversation flow for complex requests
            - I remember our conversation context automatically
            
            **Powered by OpenRouter AI**
            - Using Claude 3.5 Sonnet for intelligent responses
            - Full conversation context maintained throughout our chat
            """)

def _handle_quick_action(message: str, conv_manager: ConversationManager):
    """Handle quick action button clicks."""
    add_to_chat_history("user", message)
    conv_manager.add_user_message(message)
    
    # Get updated chat history after adding user message
    updated_chat_history = st.session_state.get('chat_history', [])
    response = call_openrouter_api(
        message, 
        conversation_history=updated_chat_history,
        conversation_state=conv_manager.get_conversation_state()
    )
    
    add_to_chat_history("assistant", response)
    conv_manager.add_assistant_message(response)
    st.rerun()

def _show_chat_history_page():
    """Display chat history page."""
    st.header("📚 Chat History")
    
    # Back button
    if st.button("← Back to Chat", key="back_to_chat_btn"):
        st.session_state.show_chat_history = False
        st.rerun()
    
    username = st.session_state.get('username', '')
    print(f"Loading chat history for user: {username}")
    
    if not username:
        st.error("No user logged in")
        return
    
    # Get chat history from database with loading indicator
    with st.spinner("Loading chat history..."):
        chat_sessions = db_manager.get_chat_history(username)
        print(f"Retrieved {len(chat_sessions)} chat sessions")
    
    if not chat_sessions:
        st.info("📭 No previous chat sessions found.")
        
        # Debug information
        with st.expander("🔍 Debug Info"):
            st.write(f"Username: {username}")
            st.write(f"Current chat length: {len(st.session_state.get('chat_history', []))}")
            
            # Test database connection
            try:
                user_data = db_manager.get_user_by_username(username)
                if user_data:
                    st.write(f"User found in database: {user_data.get('name', 'N/A')}")
                    st.write(f"User ID: {user_data.get('id', 'N/A')}")
                    
                    # Test direct database query
                    with db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = %s", (user_data['id'],))
                            count = cursor.fetchone()[0]
                            st.write(f"Chat history records in database: {count}")
                else:
                    st.write("User not found in database")
            except Exception as e:
                st.write(f"Database error: {e}")
                import traceback
                st.code(traceback.format_exc())
        return
    
    st.markdown("### Your Previous Conversations")
    
    # Display each chat session
    for i, session in enumerate(chat_sessions):
        # Handle both string and dict session_data
        session_data = session['session_data']
        if isinstance(session_data, str):
            try:
                session_data = json.loads(session_data)
            except json.JSONDecodeError:
                st.error(f"Invalid session data format for session {i+1}")
                continue
        
        created_at = session['created_at']
        message_count = session['message_count']
        
        # Create expandable section for each session
        with st.expander(
            f"📅 {created_at.strftime('%Y-%m-%d %H:%M')} - "
            f"{session_data.get('conversation_summary', 'General Conversation')} "
            f"({message_count} messages)"
        ):
            # Display conversation messages
            messages = session_data.get('messages', [])
            if not messages:
                st.info("No messages found in this session")
                continue
                
            for message in messages:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        padding: 0.8rem;
                        border-radius: 8px;
                        margin: 0.3rem 0;
                        border-left: 3px solid #2196f3;
                        color: #1565c0;
                        margin-left: 1rem;
                    ">
                        👤 <strong>You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                        padding: 0.8rem;
                        border-radius: 8px;
                        margin: 0.3rem 0;
                        border-left: 3px solid #9c27b0;
                        color: #6a1b9a;
                        margin-right: 1rem;
                    ">
                        🤖 <strong>Assistant:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Delete all history button
    st.markdown("---")
    if st.button("🗑️ Delete All Chat History", key="delete_all_history_btn", type="secondary"):
        with st.spinner("Deleting chat history..."):
            if db_manager.delete_chat_history(username):
                st.success("✅ All chat history deleted successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to delete chat history")