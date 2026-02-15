from utils import Vector_store_service
from utils.pg_memory import pg_memory
from db import get_db
from model import llm
import hashlib
import uuid


RAG_SYSTEM_PROMPT = (
            """You are a strict policy assistant.

    You MUST answer only using the provided knowledge base context.

    You are NOT a general hotel chatbot.
    You are NOT allowed to:
    - Ask follow-up questions
    - Offer services
    - Suggest bookings
    - Add extra details
    - Use marketing language
    - Make assumptions

    If the answer is not explicitly present in the knowledge base context,
    respond EXACTLY with:
    "I don't have that information. Let me connect you to a human agent."

    Do not soften the refusal.
    Do not provide partial guesses.
    Answer concisely.
"""

)


class rag_node:
    def __init__(self):
        self.llm = llm
        

    def build_context(self, retrieval_results):
        """Deduplicate and format retrieved documents."""
        if not retrieval_results.get("results"):
            return ""
        seen = set()
        context_blocks = []

        for r in retrieval_results["results"]:
            content = r["content"].strip()
            fingerprint = hashlib.md5(content.encode()).hexdigest()

            if fingerprint in seen:
                continue
            
            seen.add(fingerprint)
            context_blocks.append(content)

        return "\n\n".join(context_blocks)

    def enhance_query_with_history(self, query: str, history: list) -> str:
        """Enhance vague queries using conversation history."""
        vague_queries = [
            "tell me more", "more", "continue", "go on", "explain",
            "what else", "and?", "elaborate", "details", "more details",
            "what did i ask", "what did you say", "repeat"
        ]
        
        if query.lower().strip() in vague_queries or len(query.split()) <= 3:
            if history:
                # Get last user message for context
                for msg in reversed(history):
                    if msg.get("role") == "user":
                        return f"{msg['content']} {query}"
        return query

    def rag_node(self, state: dict):
        """
        RAG node - retrieves context and generates response.
        Uses PostgreSQL memory for persistent history management.
        """
        print("rag node executed")
        query = state.get("message", "").strip()
        org_id = state.get("org_id", "default")
        thread_id = state.get("thread_id", str(uuid.uuid4()))
        
        if not query:
            return {
                **state,
                "result": {
                    "status": "failed",
                    "response": "Query cannot be empty.",
                    "confidence": 0.0
                }
            }
        
        try:
            with get_db() as db:
                # Get or create conversation in PostgreSQL
                conversation = pg_memory.get_or_create_conversation(
                    db, thread_id, org_id
                )
                
                # Get history from PostgreSQL
                history = pg_memory.get_history(db, conversation.id, max_turns=4)
                formatted_history = pg_memory.format_for_llm(history)
                
                # Enhance query with history for better retrieval
                enhanced_query = self.enhance_query_with_history(query, history)
                
                # Retrieve from vector store using enhanced query
                vector_store = Vector_store_service(org_id)
                retrieved = vector_store.retrieve_documents(query=enhanced_query)
            
                if retrieved.get("status") != "success":
                    response_text = "Knowledge base temporarily unavailable."
                    # Save exchange to PostgreSQL
                    pg_memory.add_exchange(db, conversation.id, query, response_text)
                    return {
                        **state,
                        "result": {
                            "status": "error",
                            "response": response_text,
                            "confidence": 0.0
                        }
                    }
                
                # Even with no docs, if we have history, let LLM try to help
                context = self.build_context(retrieved)
                
                if retrieved.get("filtered_count", 0) == 0 and not history:
                    response_text = (
                        "I don't have that information. "
                        "Let me connect you to a human agent."
                    )
                    # Save exchange to PostgreSQL
                    pg_memory.add_exchange(db, conversation.id, query, response_text)
                    return {
                        **state,
                        "result": {
                            "status": "no_context",
                            "response": response_text,
                            "confidence": 0.3
                        }
                    }
                
                # Build messages using pg_memory utility
                messages = pg_memory.build_messages(
                    query=query,
                    system_prompt=RAG_SYSTEM_PROMPT,
                    history=formatted_history,
                    context=context if context else "No additional context available."
                )
                
                # Generate response
                response = self.llm.invoke(messages)
                answer = response.content if hasattr(response, "content") else str(response)
                
                # Save exchange to PostgreSQL
                pg_memory.add_exchange(db, conversation.id, query, answer)
                
                # Return updated state
                return {
                    **state,
                    "result": {
                        "status": "success",
                        "response": answer,
                        "confidence": 0.9 if retrieved.get("filtered_count", 0) >= 2 else 0.7,
                        "intent": "INFORMATION_RETRIEVAL"
                    }
                }
            
        except Exception as e:
            response_text = (
                "I'm experiencing technical difficulty. "
                "Let me connect you to a human agent."
            )
            return {
                **state,
                "result": {
                    "status": "error",
                    "response": response_text,
                    "error": str(e),
                    "confidence": 0.0
                }
            }