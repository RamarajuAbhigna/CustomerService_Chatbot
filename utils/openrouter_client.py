"""OpenRouter API client for AI chatbot functionality."""

import requests
import streamlit as st
from typing import Dict, Optional, List
from config import (
    OPENROUTER_API_URL, 
    OPENROUTER_MODEL, 
    OPENROUTER_API_KEY, 
    OPENROUTER_SITE_URL, 
    OPENROUTER_APP_NAME
)
from utils.auth import get_user_data


def call_openrouter_api(prompt: str, conversation_history: List[Dict] = None, conversation_state: Dict = None) -> str:
    """Call OpenRouter API for AI responses."""
    # Check if API key is properly configured
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.strip() == "your_openrouter_api_key_here" or OPENROUTER_API_KEY.strip() == "":
        return "⚠️ OpenRouter API key not configured. Please add your API key to config.py"

    # Get user data and conversation context
    user_data = get_user_data(st.session_state.get('username', ''))
    conversation_history = conversation_history or []
    conversation_state = conversation_state or {}
    
    # Build system message with user context
    system_message = f"""You are a helpful customer service AI for QuickDeliver, a food delivery app.

    User Information:
    - Name: {user_data.get('name', 'N/A')}
    - Subscription: {user_data.get('subscription', 'N/A')}
    - Total Orders: {len(user_data.get('orders', []))}
    
    Current Conversation Context:
    - Topic: {conversation_state.get('current_topic', 'General')}
    - Message Count: {conversation_state.get('message_count', 0)}
    
    Recent Orders (for reference):
    {_format_recent_orders(user_data.get('orders', [])[:3])}

    You can help with:
    - Order tracking and issues
    - Refund processing (ask for order ID, reason, then process)
    - Subscription management
    - Billing questions
    - Restaurant recommendations
    - Account settings
    - General support

    IMPORTANT: 
    - Maintain conversation context and don't repeat questions already answered
    - For refunds: Ask for order ID → Ask for reason → Process refund (don't loop back)
    - Be conversational and remember what was discussed earlier
    - Provide specific, actionable responses based on the conversation flow
    """

    # Build messages array with conversation history
    messages = [{"role": "system", "content": system_message}]
    
    # Add conversation history (last 10 messages to avoid token limits)
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    for msg in recent_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": OPENROUTER_SITE_URL,  # Optional, for including your app on openrouter.ai rankings
            "X-Title": OPENROUTER_APP_NAME,  # Optional, shows in rankings on openrouter.ai
        }

        data = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            error_detail = ""
            try:
                error_json = response.json()
                error_detail = error_json.get('error', {}).get('message', response.text)
            except:
                error_detail = response.text
            return f"❌ Error: {response.status_code} - {error_detail}"

    except requests.exceptions.RequestException as e:
        return f"❌ Network error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def _format_recent_orders(orders: List[Dict]) -> str:
    """Format recent orders for context."""
    if not orders:
        return "No recent orders"
    
    formatted = []
    for order in orders:
        formatted.append(f"- Order #{order.get('id', 'N/A')}: {order.get('restaurant', 'N/A')} - ₹{order.get('total', 0)} ({order.get('status', 'N/A')})")
    
    return "\n".join(formatted)


def get_quick_response(query_type: str) -> str:
    """Get quick responses for common queries."""
    quick_responses = {
        "track_order": "I want to track my recent order status",
        "billing_help": "I have a question about my monthly bill",
        "restaurant_recs": "Can you recommend some restaurants based on my order history?",
        "account_settings": "Help me with my account settings and preferences"
    }

    if query_type in quick_responses:
        return call_openrouter_api(quick_responses[query_type])

    return "I'm here to help! What can I assist you with today?"


def format_chat_message(role: str, content: str) -> Dict[str, str]:
    """Format chat message for display."""
    return {
        "role": role,
        "content": content
    }


def clear_chat_history() -> None:
    """Clear chat history from session state."""
    st.session_state.chat_history = []


def add_to_chat_history(role: str, content: str) -> None:
    """Add message to chat history."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })


def get_available_models() -> list:
    """Get list of available models from OpenRouter."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            return [model['id'] for model in models.get('data', [])]
        else:
            return []
    except:
        return []