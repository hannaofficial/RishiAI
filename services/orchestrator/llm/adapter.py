import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_with_gemini(prompt: str) -> str:
    """
    Call Gemini (Flash 2.0) and return text response.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)

    # When Gemini streams chunks, resp.text combines everything
    return resp.text
