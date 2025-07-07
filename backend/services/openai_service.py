from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY", " ")

class GPTService:
    def __init__(self, model_name="gpt-4o"):
        self.model_name = model_name
        self.system_prompt = (
            "You are a culturally sensitive Omani Arabic mental health assistant. "
            "Speak in Omani dialect, be empathetic, and integrate Islamic/Gulf values when appropriate."
        )

    def generate_response(self, user_input: str, emotion: str = None) -> str:
        user_message = f"[Emotion: {emotion}] {user_input}" if emotion else user_input
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response['choices'][0]['message']['content']