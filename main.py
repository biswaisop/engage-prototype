# main.py
from graph import graph
import uuid

def main():
    """
    Run chatbot with persistent memory using thread_id.
    Each thread_id maintains its own conversation history.
    """
    # Generate unique thread ID per conversation session
    # In production: use user_id, session_id, or conversation_id
    thread_id = str(uuid.uuid4())
    org_id = "test-org-2"
    print("Hotel Front Desk Bot (type 'quit' to exit)")
    print(f"Session: {thread_id[:8]}...")
    print("-" * 40)
    
    while True:
        message = input("\nYou: ").strip()
        if not message:
            continue
        if message.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        
        # Invoke graph with thread_id config for memory persistence
        result = graph.invoke(
            {"message": message, "org_id": org_id},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        # Extract response
        response = result.get("result", {}).get("response", "No response")
        print(f"\nBot: {response}")


if __name__ == "__main__":
    main()
