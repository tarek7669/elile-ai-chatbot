"""Emotion detection service for Arabic text."""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import Dict, Optional
from config import CONFIG

logger = logging.getLogger(__name__)

class EmotionService:
    """Emotion detection service for Arabic text."""
    
    def __init__(self):
        self.model_name = CONFIG.emotion_model_name
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the emotion detection model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            logger.info(f"Emotion model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading emotion model: {str(e)}")
            # Fallback to rule-based emotion detection
            self.tokenizer = None
            self.model = None
    
    def detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotion from Arabic text."""
        if not text:
            return {"neutral": 1.0}
        
        try:
            if self.model and self.tokenizer:
                return self._model_based_detection(text)
            else:
                return self._rule_based_detection(text)
        except Exception as e:
            logger.error(f"Error in emotion detection: {str(e)}")
            return {"neutral": 1.0}
    
    def _model_based_detection(self, text: str) -> Dict[str, float]:
        """Use transformer model for emotion detection."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Map model outputs to emotion labels
        emotion_labels = ["negative", "neutral", "positive"]
        emotions = {}
        
        for i, label in enumerate(emotion_labels):
            emotions[label] = float(predictions[0][i])
        
        return emotions
    
    def _rule_based_detection(self, text: str) -> Dict[str, float]:
        """Fallback rule-based emotion detection."""
        text_lower = text.lower()
        
        # Arabic emotion keywords
        positive_keywords = ["سعيد", "فرحان", "راضي", "ممتاز", "جيد", "أحب"]
        negative_keywords = ["حزين", "غاضب", "خائف", "قلق", "متوتر", "مكتئب"]
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {"neutral": 1.0}
        
        return {
            "positive": positive_count / total_count,
            "negative": negative_count / total_count,
            "neutral": 0.1
        }