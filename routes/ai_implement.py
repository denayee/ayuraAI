import os
from google import genai
from dotenv import load_dotenv
from flask import Blueprint

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ai_implement = Blueprint("ai", __name__)


def get_ai_recommendation():
    """Generates AI recommendation for cosmetic products."""
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="how to arrange all cosmatic product",
        )
        return response.text
    except Exception as e:
        print(f"Error generating AI content: {e}")
        return "Sorry, I couldn't generate a recommendation at this time."
