# utils/memory.py
"""
Universal memory utility for all graph nodes.
Provides efficient conversation history management.
"""
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class ConversationMemory:
    """
    Shared memory interface for all nodes.
    Handles history formatting, truncation, and message building.
    """
    
    @staticmethod
    def get_history(state: dict, max_turns: int = 6) -> List[Dict[str, str]]:
        """
        Extract conversation history from state.
        Returns last `max_turns` exchanges (user + assistant pairs).
        """
        messages = state.get("messages", [])
        if not messages:
            return []
        
        # Keep last max_turns * 2 messages (pairs of user/assistant)
        return messages[-(max_turns * 2):]
    
    @staticmethod
    def format_for_llm(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format history for LLM consumption.
        Returns messages in standard role/content format.
        """
        formatted = []
        for msg in history:
            if isinstance(msg, dict):
                formatted.append(msg)
            elif hasattr(msg, 'type') and hasattr(msg, 'content'):
                # Handle LangChain message objects
                role = "assistant" if msg.type == "ai" else msg.type
                formatted.append({"role": role, "content": msg.content})
        return formatted
    
    @staticmethod
    def build_messages(
        query: str,
        system_prompt: str,
        history: List[Dict[str, str]] = None,
        context: str = None
    ) -> List[Dict[str, str]]:
        """
        Build complete message list for LLM invocation.
        Used by all nodes for consistent message formatting.
        """
        messages = []
        
        # System prompt
        messages.append({"role": "system", "content": system_prompt})
        
        # Add context if provided (for RAG)
        if context:
            messages.append({
                "role": "system", 
                "content": f"Knowledge Base Context:\n{context}"
            })
        
        # Add conversation history
        if history:
            messages.extend(history)
        
        # Add current user query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    @staticmethod
    def add_to_history(
        state: dict,
        user_message: str,
        assistant_response: str
    ) -> List[Dict[str, str]]:
        """
        Create updated history with new exchange.
        Returns new history list (does not mutate state).
        """
        current = state.get("messages", [])
        new_messages = current + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ]
        return new_messages


# Singleton instance for easy import
memory = ConversationMemory()
