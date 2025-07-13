# Architecture Documentation: Omani AI Therapist

## 1. Introduction

This document provides a comprehensive overview of the **Omani AI Therapist** system architecture. It details the main components, data flow, and model integrations used to deliver culturally grounded therapeutic support aligned with Omani values and Islamic principles.

The Omani AI Therapist is a Streamlit-based web application designed to offer culturally aware mental health guidance and counseling.

---

## 2. System Overview

The system follows a modular architecture with clearly separated responsibilities to ensure maintainability and clarity.

### 2.1 System Architecture Diagram

```mermaid
graph TD
    A[User] -->|Voice/Text Input| B(User Interface - Streamlit)
    B -->|User Text| C{Emotion Detection Unit}
    B -->|User Text| D(Session Manager)
    C -->|Primary Emotion, Confidence| D
    D -->|Session History, Crisis Status, Emotions| E(Prompt Generator)
    E -->|Full Therapeutic Prompt| F[Large Language Model (LLM)]
    F -->|AI Text Response| B
    B -->|Voice Response (Optional)| G[Text-to-Speech Unit]
    G --> H[User]
```

### Diagram Explanation:

- **User**: Interacts via voice or text input.
- **User Interface (Streamlit)**: The front-end web app that receives input and displays responses.
- **Emotion Detection Unit**: Detects primary emotional tone (positive, negative, neutral) with confidence scores.
- **Session Manager**: Tracks conversation state, emotion, and whether a crisis is detected.
- **Prompt Generator**: Crafts full therapeutic prompts with cultural and emotional context.
- **Large Language Model (LLM)**: Produces the therapeutic response.
- **Text-to-Speech Unit**: Optionally converts response to audio and plays it back to the user.

---

## 3. Component Descriptions

### 3.1 User Interface
- **Technology**: Streamlit
- **Role**: Provides a live interface to interact via text or speech.
- **Functions**: 
  - Accepts user input
  - Displays model output
  - Plays audio via TTS if enabled

---

### 3.2 Emotion Detection Unit
- **Role**: Analyzes input to classify emotional state
- **Methodology**: _[e.g., uses Arabic sentiment classifier or HuggingFace transformers model]_
- **Outputs**:
  - `primary_emotion`: `"positive"`, `"negative"`, `"neutral"`
  - `confidence`: Float score from model

---

### 3.3 Session Manager
- **Role**: Maintains conversational state
- **Tracks**:
  - `session_history`: All dialogue turns
  - `is_crisis`: Crisis flag (bool)
  - `primary_emotion`, `confidence`
- **Storage**: _[e.g., Streamlit session memory using `st.session_state`]_

---

### 3.4 Prompt Generator (`_create_therapeutic_prompt`)
- **Role**: Constructs full therapeutic prompt
- **Includes**:
  - Therapist personality instructions
  - Cultural/religious sensitivity guidelines
  - Emotion-specific responses
  - Crisis flag
  - Past turns (`session_history`)
  - Few-shot examples

---

### 3.5 Large Language Model (LLM)
- **Model**: _[e.g., GPT-4o, Gemini 1.5 Flash]_
- **Role**: Generates culturally and emotionally aware responses in Arabic
- **Integration**: _[e.g., via `openai` or `google-generativeai` API client libraries]_

---

### 3.6 Text-to-Speech Unit (Optional)
- **Technology**: _[e.g., Coqui XTTS, WebSpeech API, gTTS]_
- **Role**: Converts text to spoken voice response
- **Format**: WAV/MP3 played directly in browser

---

## 4. Data Flow

1. **User Input**: User types or speaks a message.
2. **Emotion Analysis**: Emotion model analyzes emotional tone.
3. **Session State Update**: Conversation, emotion, and crisis flags are stored.
4. **Prompt Generation**: All context and constraints are compiled into a prompt.
5. **LLM Response**: Model generates response based on cultural and emotional context.
6. **Display/Playback**: Output is displayed and optionally spoken.
7. **Log Turn**: Result added to `session_history`.

---

## 5. Key Architectural Decisions and Challenges

- **Session State in Streamlit**: Simple to use but non-persistent; resets on reload unless extended.
- **Component Isolation**: Clear separation between logic and UI for modularity.
- **LLM Choice**: Heavily impacts Arabic understanding, latency, and cost. Selection was made based on _[reasons: performance, Arabic support, cost]_.
- **Crisis Detection**: Built-in logic to surface emergency help if triggered, but not a replacement for real therapy.

---

## 6. Conclusion

The Omani AI Therapist architecture is modular, efficient, and highly adaptable. It allows flexible updates to components like LLMs, emotion models, and TTS systems while ensuring cultural and ethical integrity.
