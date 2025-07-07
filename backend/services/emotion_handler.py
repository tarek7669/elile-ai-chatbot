from transformers import pipeline

class EmotionDetector:
    def __init__(self, model_name="bhavsar97/emotion-classification-arabic"):
        self.model = pipeline("text-classification", model=model_name, top_k=1)

    def detect(self, text: str) -> dict:
        result = self.model(text)[0]
        return {
            "emotion": result["label"],
            "score": result["score"]
        }