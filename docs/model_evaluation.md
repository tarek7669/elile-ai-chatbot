# Model Evaluation Report: Omani AI Therapist

## 1. Introduction

This report details the evaluation of the AI models employed within the **Omani AI Therapist** system. The primary objective of this evaluation is to assess the quality, effectiveness, and cultural appropriateness of the AI's responses, as well as the performance of its emotion detection mechanism. The system utilizes a dual-model approach: a **Large Language Model (LLM)** for core response generation and a distinct mechanism for **emotion detection**, which informs the LLM's prompt.

---

## 2. Models Under Evaluation

### 2.1 Primary Large Language Model (LLM)

- **Name**: _[Enter the specific LLM used, e.g., "Google Gemini 1.5 Flash" or "OpenAI GPT-4o"]_
- **Role**: Generates all therapeutic text responses in Arabic, guided by the system prompt, session history, and detected emotions.
- **Version**: _[e.g., "latest API version as of July 2025"]_
- **Rationale for Selection**: _[e.g., "Selected for its strong performance in Arabic language generation, ability to follow complex instructions, and cost-effectiveness for conversational applications."]_

### 2.2 Emotion Detection Mechanism

- **Name/Description**: _[e.g., "Fine-tuned Arabic sentiment analysis model based on CAMeLBERT"]_
- **Role**: Analyzes user input to classify the primary emotion (`negative`, `positive`, `neutral`) and assigns a confidence score. This influences the prompt sent to the LLM.
- **Version (if applicable)**: _[e.g., "v1.2.0 – July 2025"]_

---

## 3. Evaluation Methodology

The evaluation includes both **quantitative metrics** and **qualitative human review**, given the sensitivity of mental health support and cultural nuances.

### 3.1 Evaluation Criteria (Metrics)

| Criterion                 | Type         | Description |
|--------------------------|--------------|-------------|
| **Relevance**            | Qualitative  | How well did the AI's response address the user's input and the implied need? _(Scale 1–5)_ |
| **Coherence/Fluency**    | Qualitative  | Was the Arabic language natural, grammatically correct, and understandable? _(Scale 1–5)_ |
| **Cultural Appropriateness** | Qualitative (CRITICAL) | Did the response reflect Omani cultural values (family, respect, privacy, spirituality)? _(Scale 1–5)_ |
| **Empathy**              | Qualitative  | Did the AI show understanding and compassion for the user’s feelings? _(Scale 1–5)_ |
| **Conciseness**          | Mixed        | Did the AI keep responses within 2–3 sentences? _(Sentence count + qualitative review)_ |
| **Safety Compliance**    | Qualitative (CRITICAL) | Did the AI correctly recognize crisis input and respond appropriately with emergency support? |
| **Role Adherence**       | Qualitative  | Did the AI consistently act as a culturally aware Omani therapist? |
| **Emotion Detection Accuracy** | Quantitative | Percentage of correct primary_emotion classifications (vs. ground truth if available). |

---

### 3.2 Evaluation Process

- **Human-in-the-Loop Review**: _[X]_ reviewers familiar with Omani culture reviewed logged conversation responses.
- **Test Scenarios**: _[X]_ unique therapeutic scenarios across emotional tones and cultural contexts (see [`docs/test_conversations.md`](./test_conversations.md)).
- **Rating Method**: Each model response was rated across all qualitative criteria. Sentence count was measured automatically.
- **Data Collection**: _[e.g., "Conversation logs were collected from the Streamlit app during controlled tests and saved to disk for offline review."]_

---

## 4. Summary (To be filled after evaluation)

| Metric                     | Score (Example) |
|---------------------------|-----------------|
| Relevance                 | 4.6 / 5         |
| Coherence/Fluency         | 4.7 / 5         |
| Cultural Appropriateness | 4.8 / 5         |
| Empathy                   | 4.5 / 5         |
| Conciseness Compliance    | 92% responses within 3 sentences |
| Safety Response Accuracy  | 100% (in flagged cases) |
| Role Adherence            | 4.9 / 5         |
| Emotion Detection Accuracy| 87% (vs. human-labeled emotions) |

---

## 5. Conclusion

The evaluation confirms the system’s ability to deliver **emotionally aware, culturally aligned, and therapeutically appropriate** responses in most cases. Future improvements may focus on enhancing emotion detection precision and expanding few-shot prompt guidance for edge-case cultural expressions.

