from utils import Vector_store_service
from model import llm
import hashlib
class rag_node:
    def __init__(self):
        self.llm = llm

    def format_history(self, history, max_turns = 4):
        if not history:
            return []
        return history [-max_turns]

    def build_context(self, retrieval_results):
        if not retrieval_results["results"]:
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
    
    def build_messages(self, query, context, history):
        messages = []

        messages.append({
            "role": "system",
            "content": (
                "You are a helpful assistant for a business. "
                "Answer ONLY using the provided knowledge base context. "
                "If the answer is not in the context, say: "
                "'I don't have that information. Let me connect you to a human agent.' "
                "Do NOT fabricate information."
            )
        })

        messages.append({
            "role": "system",
            "content": f"Knowledge Base Context:\n{context}"
        })

        messages.extend(history)

        messages.append({
            "role":"user",
            "content": query
        })

        return messages

    def rag_node(self, query:str, state: dict, org_id: str, history):
        if not query or not query.strip():
            return {
                "status": "failed",
                "message": "Query cannot be empty."
            }
        try:
            vector_store = Vector_store_service(org_id)
            retrieved = vector_store.retrieve_documents(query=query)
            if retrieved["staus"] != "success":
                return {
                    "status": "error",
                    "message": "knowledge base temporarily unavailable"
                }
            if retrieved["filtered_count"] == 0:
                return {
                    "status": "no_context",
                    "message": (
                        "I dont have that information. "
                        "Let me connect you to a human agent. "
                    ),
                    "confidence":"low"
                }
            context = self.build_context(retrieval_results=retrieved)
            formatted_history = self.format_history(history)
            messages = self.build_messages(
                query=query,
                context=context,
                history = formatted_history
            )
            response = self.llm.invoke(messages)

            if hasattr(response, "content"):
                answer = response.content
            else:
                answer = str(response)
            return {
                "status": "success",
                "answer": answer,
                "confidence": (
                    "high" if retrieved["filtered_count"] >= 2 else "medium"
                )
            }
        except Exception as e: 
            return {
                "status": "error",
                "message": (
                    "I'm experiencing technical difficulty. "
                    "Let me connect you to a human agent."
                ),
                "error": str(e)
            }
            

    




