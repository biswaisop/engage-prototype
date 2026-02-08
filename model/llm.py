from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
load_dotenv()

# gemini = os.getenv('GEMINI_API_KEY')
groq = os.getenv('GROQ_LLM_KEY')

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=gemini
# )

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)