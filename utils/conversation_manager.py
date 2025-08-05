"""Conversation manager to handle chat context and flow."""

from typing import Dict, List, Optional
import json
from datetime import datetime


class ConversationManager:
    """Manages conversation context and flow for better chatbot responses."""
    
    def __init__(self):
        self.conversation_state = {
            'current_topic': None,
            'context': {},
            'message_count': 0,
            'last_user_message': None,
            'last_assistant_message': None,
            'conversation_flow': []
        }
    
    def add_user_message(self, message: str):
        """Add user message and update conversation state."""
        self.conversation_state['last_user_message'] = message
        self.conversation_state['message_count'] += 1
        
        # Detect conversation topic
        topic = self._detect_topic(message)
        if topic:
            self.conversation_state['current_topic'] = topic
        
        # Add to conversation flow
        self.conversation_state['conversation_flow'].append({
            'role': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'topic': topic
        })
    
    def add_assistant_message(self, message: str):
        """Add assistant message and update conversation state."""
        self.conversation_state['last_assistant_message'] = message
        
        # Add to conversation flow
        self.conversation_state['conversation_flow'].append({
            'role': 'assistant',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'topic': self.conversation_state.get('current_topic')
        })
    
    def _detect_topic(self, message: str) -> Optional[str]:
        """Detect conversation topic from user message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['refund', 'return', 'money back', 'cancel order']):
            return 'refund_request'
        elif any(word in message_lower for word in ['track', 'order status', 'delivery', 'where is my order']):
            return 'order_tracking'
        elif any(word in message_lower for word in ['bill', 'payment', 'charge', 'subscription']):
            return 'billing_inquiry'
        elif any(word in message_lower for word in ['recommend', 'suggest', 'restaurant', 'food']):
            return 'recommendations'
        elif any(word in message_lower for word in ['account', 'profile', 'settings', 'password']):
            return 'account_management'
        
        return None
    
    def get_conversation_state(self) -> Dict:
        """Get current conversation state."""
        return self.conversation_state.copy()
    
    def get_current_topic(self) -> Optional[str]:
        """Get current conversation topic."""
        return self.conversation_state.get('current_topic')
    
    def get_topic_message_count(self) -> int:
        """Get number of messages in current topic."""
        current_topic = self.get_current_topic()
        if not current_topic:
            return 0
        
        count = 0
        for flow_item in self.conversation_state['conversation_flow']:
            if flow_item.get('topic') == current_topic:
                count += 1
        return count
    
    def reset_conversation(self):
        """Reset conversation state."""
        self.conversation_state = {
            'current_topic': None,
            'context': {},
            'message_count': 0,
            'last_user_message': None,
            'last_assistant_message': None,
            'conversation_flow': []
        }
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.conversation_state['conversation_flow']:
            return "General Conversation"
        
        topics = set()
        for flow_item in self.conversation_state['conversation_flow']:
            if flow_item.get('topic'):
                topics.add(flow_item['topic'])
        
        if topics:
            return ', '.join(topics).replace('_', ' ').title()
        
        return "General Conversation"