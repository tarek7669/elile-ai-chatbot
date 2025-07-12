"""GPT service with Claude fallback for therapeutic responses."""

import openai
import anthropic
import logging
from typing import Optional, Dict
from config import CONFIG
from utils.text_utils import detect_crisis_keywords

logger = logging.getLogger(__name__)

class GPTService:
    """GPT service with Claude fallback for therapeutic responses."""
    
    def __init__(self):
        openai.api_key = CONFIG.openai_api_key
        self.anthropic_client = anthropic.Anthropic(api_key=CONFIG.anthropic_api_key)
    
    def generate_therapeutic_response(self, 
                                    user_text: str, 
                                    emotion_data: Optional[Dict[str, float]] = None) -> Optional[str]:
        """Generate therapeutic response using GPT-4 with Claude validation."""
        
        # Check for crisis keywords
        is_crisis = detect_crisis_keywords(user_text, CONFIG.crisis_keywords)
        
        try:
            # Generate response with GPT-4
            gpt_response = self._generate_gpt_response(user_text, is_crisis, emotion_data)
            
            return gpt_response
            # if gpt_response:
            #     # Validate with Claude
            #     validated_response = self._validate_with_claude(gpt_response, user_text, is_crisis)
            #     return validated_response or gpt_response
            
            # Fallback to Claude if GPT fails
            # return self._generate_claude_response(user_text, emotion_data, is_crisis)
            
        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return self._generate_fallback_response(is_crisis)
    
    def _generate_gpt_response(self, 
                             user_text: str, 
                             is_crisis: bool,
                             emotion_data: Optional[Dict[str, float]] = None) -> Optional[str]:
        """Generate response using GPT-4."""
        
        # Determine primary emotion
        primary_emotion = max(emotion_data, key=emotion_data.get)
        emotion_confidence = emotion_data[primary_emotion]
        
        # Create therapeutic prompt
        system_prompt = self._create_therapeutic_prompt(is_crisis, 
                                                       primary_emotion, 
                                                       emotion_confidence)
        
        try:
            response = openai.ChatCompletion.create(
                model=CONFIG.gpt_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error with GPT-4: {str(e)}")
            return None
    
    def _validate_with_claude(self, 
                            gpt_response: str, 
                            user_text: str, 
                            is_crisis: bool) -> Optional[str]:
        """Validate GPT response using Claude."""
        
        validation_prompt = f"""
        You are validating a therapeutic response for cultural appropriateness and safety.
        
        User input: {user_text}
        GPT Response: {gpt_response}
        Crisis situation: {is_crisis}
        
        Please:
        1. Ensure the response is culturally appropriate for Omani/Gulf Arabic culture
        2. Verify it follows Islamic values and family-centered approach
        3. Check for therapeutic appropriateness
        4. If crisis situation, ensure proper safety protocols
        
        Respond with either:
        - "APPROVED" if the response is appropriate
        - Provide an improved version in Omani dialect if changes are needed
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=CONFIG.claude_model,
                max_tokens=400,
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            claude_response = response.content[0].text.strip()
            
            if claude_response.startswith("APPROVED"):
                return None  # GPT response is approved
            else:
                return claude_response  # Use Claude's improved version
                
        except Exception as e:
            logger.error(f"Error validating with Claude: {str(e)}")
            return None
    
    def _generate_claude_response(self, 
                                user_text: str, 
                                emotion_data: Dict[str, float], 
                                is_crisis: bool) -> Optional[str]:
        """Generate response using Claude as fallback."""
        
        primary_emotion = max(emotion_data, key=emotion_data.get)
        
        prompt = f"""
        You are an AI therapist specializing in Omani/Gulf Arabic culture. 
        
        User said: {user_text}
        Detected emotion: {primary_emotion}
        Crisis situation: {is_crisis}
        
        Please provide a therapeutic response in Omani dialect that:
        - Shows empathy and understanding
        - Respects Islamic values and family importance
        - Uses appropriate Omani dialect expressions
        - Provides practical, culturally-sensitive advice
        {"- Includes crisis intervention if needed" if is_crisis else ""}
        
        Response should be 2-3 sentences maximum.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=CONFIG.claude_model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error with Claude: {str(e)}")
            return None
    
    def _create_therapeutic_prompt(self,
                                 is_crisis: bool, 
                                 primary_emotion: str = None, 
                                 confidence: float = None) -> str:
        """Create therapeutic system prompt."""
        
        base_prompt = """
        You are a professional AI therapist specializing in Omani/Gulf Arabic culture. 
        
        Key principles:
        - Respond ONLY in Omani dialect Arabic
        - Integrate Islamic values and family-centered approach
        - Use cognitive-behavioral therapy techniques
        - Be empathetic and culturally sensitive
        - Keep responses concise (2-3 sentences max)
        """
        
        emotion_guidance = {
            "negative": "Show deep empathy. Acknowledge their pain. Offer hope and practical coping strategies.",
            "positive": "Celebrate their positive feelings. Encourage gratitude and continued growth.",
            "neutral": "Gently explore their feelings. Encourage self-reflection and emotional awareness."
        }
        
        crisis_guidance = """
        CRISIS PROTOCOL:
        - Acknowledge their pain immediately
        - Provide immediate safety resources
        - Encourage professional help
        - Mention emergency contacts (16262 - Oman Mental Health)
        """
        # prompt = base_prompt
        prompt = base_prompt + f"\n\nCurrent emotion: {primary_emotion} (confidence: {confidence:.2f})\n"
        prompt += emotion_guidance.get(primary_emotion, emotion_guidance["neutral"])
        
        if is_crisis:
            prompt += f"\n\n{crisis_guidance}"
        
        return prompt
    
    def _generate_fallback_response(self, is_crisis: bool) -> str:
        """Generate fallback response when all services fail."""
        
        if is_crisis:
            return """أتفهم أنك تمر بوقت صعب جداً. من المهم أن تطلب المساعدة الفورية. 
            يرجى الاتصال بخط المساعدة النفسية في عمان على الرقم 16262 أو التوجه إلى أقرب مستشفى."""
        
        return """أعتذر، أواجه صعوبة تقنية الآن. لكن أريدك أن تعرف أنني هنا لمساعدتك. 
        كيف يمكنني أن أدعمك اليوم؟"""
