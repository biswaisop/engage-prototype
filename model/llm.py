from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
load_dotenv()

groq = os.getenv('GROQ_LLM_KEY')

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

# gemini = os.getenv("GEMINI_API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key = gemini,
#     temperature = 0
# )

if __name__ == "__main__":
    llm.invoke("hi")