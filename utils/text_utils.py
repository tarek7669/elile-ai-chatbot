"""Text processing utilities for Arabic text."""

import re
import unicodedata
from typing import str

def normalize_arabic_text(text: str) -> str:
    """Normalize Arabic text for processing."""
    if not text:
        return ""
    
    # Remove diacritics
    text = ''.join(char for char in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(char) != 'Mn')
    
    # Normalize Arabic letters
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def detect_crisis_keywords(text: str, keywords: list) -> bool:
    """Detect crisis-related keywords in text."""
    normalized_text = normalize_arabic_text(text.lower())
    
    for keyword in keywords:
        if keyword.lower() in normalized_text:
            return True
    
    return False

def is_arabic_text(text: str) -> bool:
    """Check if text contains Arabic characters."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))