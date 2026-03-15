from utils.vec_store import Vector_store_service
from model.llm import llm
import hashlib
import asyncio

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

    def enhance_query_with_history(self, query: str, context: str) -> str:
        """Enhance vague queries using conversation history."""
        vague_queries = [
            "tell me more", "more", "continue", "go on", "explain",
            "what else", "and?", "elaborate", "details", "more details",
            "what did i ask", "what did you say", "repeat"
        ]
        
        if query.lower().strip() in vague_queries or len(query.split()) <= 3:
            if context:
                # Get last user message for context
                lines = context.strip().split('\n')
                for line in reversed(lines):
                    if line.startswith('USER: '):
                        last_user_msg = line.replace('USER:', '').strip()
                        return f"{last_user_msg} {query}"
        return query

    async def rag_node(self, state: dict):
        """
        RAG node - retrieves context and generates response.
        Uses shared memory utility for efficient history management.
        """
        print("rag node executed")
        query = state.get("message", "").strip()
        org_id = state.get("org_id", "default")
        context = state.get("context", "")
        
        if not query:
            return {
                **state,
                "result": {
                    "status": "failed",
                    "response": "Query cannot be empty.",

                }
            }
        
        try:
            # Enhance query with history for better retrieval
            enhanced_query = self.enhance_query_with_history(query, context)
            
            # Retrieve from vector store using enhanced query
            vector_store = Vector_store_service(org_id)
            retrieved = await asyncio.to_thread(
                vector_store.retrieve_documents(query=enhanced_query)
            )
            
            # # Get history for LLM context
            # history = memory.get_history(state, max_turns=4)
            # formatted_history = memory.format_for_llm(history)
            
            if retrieved.get("status") != "success":
                response_text = "Knowledge base temporarily unavailable."
                return {
                    **state,
                    # "messages": memory.add_to_history(state, query, response_text),
                    "result": {
                        "status": "error",
                        "response": response_text,
                    }
                }
            
            # Even with no docs, if we have history, let LLM try to help
            doc_context = self.build_context(retrieved)
            
            if retrieved.get("filtered_count", 0) == 0 and not context:
                response_text = (
                    "I don't have that information. "
                    "Let me connect you to a human agent."
                )
                return {
                    **state,
                    # "messages": memory.add_to_history(state, query, response_text),
                    "result": {
                        "status": "no_context",
                        "response": response_text,
                    }
                }
            
            # Build messages using shared utility
            prompt = f"""Conversation history:
                {context}

                Knowledge base context:
                {doc_context if doc_context else "No additional context available."}

                User question: {query}
            """
            
            # Generate response
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, "content") else str(response)
            
            # Return updated state with new history
            return {
                **state,
                # "messages": memory.add_to_history(state, query, answer),
                "result": {
                    "status": "success",
                    "response": answer,
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
                # "messages": memory.add_to_history(state, query, response_text),
                "result": {
                    "status": "error",
                    "response": response_text,
                    "error": str(e),

                }
            }