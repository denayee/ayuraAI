import os
from google import genai
from dotenv import load_dotenv
from flask import Blueprint

load_dotenv()

ai_implement = Blueprint("ai", __name__)

# Create client using new SDK
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_recommendation(user_profile):
    """Generates AI recommendation for cosmetic products."""
    try:
        prompt = f"""
        Act as a professional Dermatologist and Hair Stylist.
        Analyze the following user profile and provide personalized recommendations.

        User Profile:
        - Skin Type: {user_profile.get("skin_type")}
        - Skin Color: {user_profile.get("skin_color")}
        - Skin Problems: {user_profile.get("skin_problems")}
        - Skin Sensitivity: {user_profile.get("sensitivity_level")}
        - Skin Oil Level: {user_profile.get("oil_level")}
        - Acne: {user_profile.get("acne_presence")} ({user_profile.get("acne_level")})
        - Skin Dryness: {user_profile.get("dryness_presence")} ({user_profile.get("dryness_level")})
        - Lifestyle: {user_profile.get("lifestyle")}

        - Hair Type: {user_profile.get("hair_type")}
        - Hair Color: {user_profile.get("hair_color")}
        - Hair Problems: {user_profile.get("hair_problems")}
        - Scalp Condition: {user_profile.get("scalp_condition")}
        - Hair Fall: {user_profile.get("hair_fall_level")}
        - Hair Dryness: {user_profile.get("hair_dryness_presence")} ({user_profile.get("hair_dryness_level")})
        - Scalp Itch: {user_profile.get("scalp_itch_presence")} ({user_profile.get("scalp_itch_level")})

        - Allergies: {user_profile.get("allergies")}

        Provide response in Markdown format with these sections:

        1. Recommended Cosmetic Products
        2. Safe Home Remedies
        3. Daily Care Routine
        4. Ingredients to Avoid
        5. Lifestyle Tips
        6. Explanation of Recommendations
        7. References (if any, provide links to studies or sources)
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        # Safe return (important)
        if response.text:
            return response.text
        else:
            return response.candidates[0].content.parts[0].text

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error generating AI content: {e}")
        return "Sorry, I couldn't generate a recommendation at this time nnnnn."
