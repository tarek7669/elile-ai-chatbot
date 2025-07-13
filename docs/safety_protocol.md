# 🛡️ Safety Protocol Documentation: Omani AI Therapist

## 1. Introduction

The "Omani AI Therapist" is designed as a supportive and guiding tool for mental well-being. However, it is crucial to establish clear safety protocols, especially when dealing with sensitive topics and potential crisis situations. This document outlines the mechanisms for crisis detection, the AI's response protocol, and the inherent limitations of the AI in providing direct crisis intervention. It explicitly states that the AI is a support tool, **not a substitute for human professionals**, especially in emergencies.

---

## 2. Crisis Detection Mechanism

The system is equipped with a mechanism to identify potential crisis indicators within user input.

### 2.1. Triggers

Crisis detection is primarily based on the presence of specific keywords, phrases, or a combination of highly negative sentiment with certain expressions that suggest self-harm, suicidal ideation, or immediate danger to self or others.

**Examples of Arabic keywords/phrases:**

- انتحار (suicide)  
- أريد أن أموت (I want to die)  
- إنهاء حياتي (ending my life)  
- أؤذي نفسي (harm myself)  
- لا أستطيع التحمل (I can't bear it)  
- سأنهي كل شيء (I will end everything)  
- سأضر (I will harm [someone/something])  
- أريد مساعدة فورية (I need immediate help - in a distress context)

### 2.2. Technology/Method

The `is_crisis` flag is determined by:

> [Enter your crisis detection method here. Examples:]  
> - A rule-based system that scans user input for predefined crisis keywords and phrases.  
> - A dedicated lightweight LLM call that classifies the input as `crisis` or `non-crisis`.  
> - A combination of sentiment analysis and keyword matching. For example, if sentiment is `negative` and crisis keywords are present, `is_crisis` is flagged.

### 2.3. Confidence Thresholds (if applicable)

> [Optional: If your system uses confidence scores]  
> e.g., "`is_crisis = True` if confidence score ≥ 0.85."

---

## 3. Crisis Response Protocol (AI's Actions)

When the `is_crisis` flag is activated, the AI’s primary objective shifts immediately to **user safety**.

### 3.1. Immediate Acknowledgment and Empathy

The AI first acknowledges the severity of the situation with empathy.

**Example:**  
`أتفهم تماماً حجم الألم الذي تشعر به.`  
_(I completely understand the magnitude of the pain you are feeling.)_

### 3.2. Prioritization of Safety Information

Emergency guidance overrides all other goals.

### 3.3. Emergency Contact Information (Oman Specific)

- **🆘 Omani Mental Health Helpline:** `16262`  
> [Optional: Add Police `9999` if physical safety is at risk.]

### 3.4. Strong Recommendation for Human Help

The AI strongly encourages seeking immediate **human** help.

**Example:**  
`في مثل هذه الحالات، من الضروري جداً التواصل مع متخصص. يرجى الاتصال بخط المساعدة النفسية في عُمان على الرقم 🆘 16262 فوراً. أنت لست وحدك.`  
_(In such cases, it is very necessary to contact a specialist. Please call the Mental Health Helpline in Oman at 🆘 16262 immediately. You are not alone.)_

### 3.5. AI’s Therapeutic Limitations in Crisis

The AI will **not** offer deep therapy or risk further distress — it will only redirect to human resources.

### 3.6. Tone in Crisis

Tone remains **calm**, **empathetic**, but also **firm** and **urgent** when needed.

---

## 4. Escalation Procedures (Human Intervention)

### 4.1. Current System’s Approach

No automated escalation to human agents or emergency services is currently implemented.

### 4.2. User Guidance

The AI focuses on **self-escalation** by the user, offering direct, actionable steps.

### 4.3. Future Considerations

Possible additions in future iterations:

- Human-in-the-loop monitoring or referral.
- Integration with Omani mental health institutions.

---

## 5. Ethical Considerations in Crisis Management

### Do No Harm

The protocol adheres to the medical ethics principle of prioritizing **no harm**.

### Responsibility & Limitations

The AI is a support tool — **not** a clinical diagnosis or treatment provider.

### Transparency

The limitations are conveyed both through:
- Response wording
- In-app disclaimers (recommended)

---

## 6. Testing & Validation of Protocol

### 6.1. Test Scenarios

> [Describe your test methodology, e.g.:]  
> "Simulated scenarios with suicidal ideation, self-harm, and severe distress were tested (see `docs/test_conversations.md`)."

### 6.2. Results

> [Example:]  
> "The AI detected 95% of crisis scenarios correctly, activated the `is_crisis` flag, and responded with emergency contact info and empathetic guidance. In 5% of cases, responses required tuning for more clarity."

---

## 7. Conclusion

The safety protocol in the Omani AI Therapist reflects a **deep commitment to ethical and responsible AI deployment** in mental health. By emphasizing immediate human referral, cultural sensitivity, and therapeutic integrity, it ensures the user’s **well-being remains the system's top priority**.
