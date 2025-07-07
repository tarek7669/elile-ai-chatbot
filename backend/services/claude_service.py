import os
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

load_dotenv()

class ClaudeService:
    def __init__(self, model="claude-3-opus-20240229"):
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def validate_response(self, gpt_reply: str) -> str:
        prompt = (
            f"{HUMAN_PROMPT} This is a GPT-4o-generated response: \"{gpt_reply}\"\n\n"
            "Please validate this reply for:\n"
            "- Cultural appropriateness (Omani/Gulf norms)\n"
            "- Emotional tone (empathetic, respectful)\n"
            "- Clinical accuracy (safe and ethical advice)\n"
            "- Islamic sensitivity (when applicable)\n"
            f"{AI_PROMPT}"
        )

        response = self.client.completions.create(
            model=self.model,
            max_tokens_to_sample=300,
            prompt=prompt
        )
        return response.completion.strip()