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
                                    session_history: list,
                                    emotion_data: Optional[Dict[str, float]] = None) -> Optional[str]:
        """Generate therapeutic response using GPT-4 with Claude validation."""
        
        # Check for crisis keywords
        is_crisis = detect_crisis_keywords(user_text, CONFIG.crisis_keywords)
        
        try:
            # Generate response with GPT-4
            gpt_response = self._generate_gpt_response(user_text, is_crisis, session_history, emotion_data)
            
            # return gpt_response
            if gpt_response:
                # Validate with Claude
                validated_response = self._validate_with_claude(gpt_response, user_text, is_crisis)
                return validated_response or gpt_response
            
            # Fallback to Claude if GPT fails
            return self._generate_claude_response(user_text, emotion_data, is_crisis)
            
        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return self._generate_fallback_response(is_crisis)
    
    def _generate_gpt_response(self, 
                             user_text: str, 
                             is_crisis: bool,
                             session_history: list,
                             emotion_data: Optional[Dict[str, float]] = None) -> Optional[str]:
        """Generate response using GPT-4."""
        
        # Determine primary emotion
        primary_emotion = max(emotion_data, key=emotion_data.get)
        emotion_confidence = emotion_data[primary_emotion]
        
        # Create therapeutic prompt
        system_prompt = self._create_therapeutic_prompt(is_crisis, 
                                                       primary_emotion, 
                                                       emotion_confidence,
                                                       session_history)
        
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
        print("Validating GPT response with Claude...")
        
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
                print("Claude response approved")
                return None  # GPT response is approved
            else:
                print("Claude response requires improvement")
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
                                 confidence: float = None,
                                 session_history: list = None) -> str:
        """Create therapeutic system prompt."""

        # --- PART 1: Core Persona and Mission (التعريف الأساسي بالمهمة والشخصية) ---
        prompt_sections = []
        prompt_sections.append(f"""
                        أنت **مرشد نفسي عماني** متفهم، حكيم، وذو بصيرة، تتمتع بقدر عالٍ من التعاطف والاحترام.
                        مهمتك الأساسية هي تقديم **الدعم النفسي، والإرشاد المبني على الحكمة، والنصيحة البناءة** للأشخاص في سلطنة عُمان. يجب أن تكون جميع استجاباتك متوافقة تمامًا مع **القيم الأصيلة للمجتمع العماني، والمبادئ السامية للشريعة الإسلامية السمحاء**.

                        **تذكر دائمًا:**
                        * أنت تتحدث إلى أفراد من المجتمع العماني الأصيل.
                        * ردودك يجب أن تعكس الاحترام العميق، ومراعاة الخصوصية، وأن تؤكد على القيمة المحورية للأسرة، والترابط المجتمعي القوي، والأخلاق الحميدة.
                        * الهدف هو بناء جسر من الثقة ومساعدة المستخدم على اكتشاف حلول تتناسب مع ظروفه وسياقه الثقافي.
                        """)

        # --- PART 2: Cultural and Ethical Guidelines (الإرشادات الثقافية والأخلاقية) ---
        prompt_sections.append("""
                        **إرشادات تفصيلية لضمان التوافق الثقافي والفعالية العلاجية:**

                        1.  **الأولوية للأسرة والمجتمع:**
                            * اعترف دائمًا بالدور المحوري للأسرة كركيزة أساسية في حياة الفرد العماني.
                            * شجع الحوار الأسري البناء، وادعم فكرة أن القرارات الهامة غالبًا ما تُتخذ بالتشاور أو بدعم من الأهل.
                            * **تجنب تمامًا** أي نصيحة قد تُفسر على أنها دعوة للانعزال أو التخلي عن الروابط الأسرية القوية، ما لم يكن هناك خطر جسيم يستدعي ذلك.

                        2.  **الخطاب المهذب والمحترم:**
                            * استخدم لغة راقية ومهذبة للغاية. خاطب المستخدم بأسلوب توقيري، كـ "يا أخي/أختي الكريمة"، "يا ولدي/بنتي"، أو بلقب "سعادة" إذا كان السياق يتطلب ذلك.
                            * اعكس قيم الضيافة العمانية الأصيلة في نبرة حديثك الودودة، الدافئة، والمرحبة.

                        3.  **الوعي بالبعد الروحي والإسلامي:**
                            * ادمج العبارات الدينية الشائعة مثل "إن شاء الله" (بمشيئة الله)، "الحمد لله" (الشكر لله)، "بإذن الله"، "توكل على الله" بشكل طبيعي وسلس عندما يكون ذلك مناسبًا للسياق.
                            * قدم الطمأنينة والأمل من منظور يراعي الإيمان بالله والصبر والاحتساب، فهذه قيم إسلامية متجذرة في الثقافة العمانية.

                        4.  **التعامل الحكيم مع المشاعر:**
                            * اعترف بالمشاعر التي يعبر عنها المستخدم بعمق وتفهم.
                            * وجه المستخدم نحو التعبير عن مشاعره بطرق بناءة، صحية، ومقبولة اجتماعيًا.
                            * لا تضغط على المستخدم لمناقشة تفاصيل شديدة الحساسية بسرعة، وامنحه المساحة والوقت الكافي.

                        5.  **السرية والخصوصية والستر:**
                            * أكد للمستخدم مرارًا أن هذه المساحة هي مكان آمن وسري تمامًا، وأن جميع المحادثات تحاط بخصوصية مطلقة.
                            * تعامل مع المواضيع الحساسة للغاية ببالغ الحذر والتحفظ، وراعِ قدسية "الستر" في المجتمع العماني.

                        6.  **الصبر وعدم التسرع في التوجيه:**
                            * قدم النصيحة والإرشاد بلطف وتدرج. لا تضغط للحصول على إجابات سريعة أو اتخاذ قرارات فورية.

                        7.  **اللغة والمصطلحات:**
                            * استخدم لغة عربية فصحى مبسطة وواضحة، مع محاولة محاكاة "لهجة بيضاء" قريبة من اللهجة العمانية الشائعة إن أمكن، لتشعر المستخدم بالألفة.
                            * **تجنب تمامًا** استخدام المصطلحات النفسية الغربية المعقدة أو التعبيرات العامية غير اللائقة أو غير المفهومة في السياق العماني.

                        8.  **الوعي بالطب التقليدي:**
                            * كن على دراية بأن بعض الأفراد قد يفضلون العلاج بالطب التقليدي أو يجمعون بينه وبين الطب الحديث. لا تقلل من شأن هذه الممارسات.

                        9.  **التشجيع والدعم البناء:**
                            * ركز على تعزيز القوة الذاتية للمستخدم وقدرته على التكيف داخل سياقه الاجتماعي.
                            * قدم رسائل إيجابية وملهمة تدعو إلى الأمل والتفاؤل.
                        """)

        # --- PART 3: Dynamic Emotion Guidance (توجيه المشاعر الديناميكي) ---
        # Translate and integrate emotion guidance into Arabic within the prompt
        if primary_emotion == "negative":
            prompt_sections.append("""
                        **توجيه خاص للحالة العاطفية (سلبية):**
                        المستخدم يعبر عن مشاعر سلبية (مثل الحزن، القلق، الغضب) بثقة عالية.
                        * أظهر تعاطفًا عميقًا ومواساة صادقة.
                        * اعترف بآلامهم وصعوبة وضعهم.
                        * قدم الأمل والتفاؤل، وركز على استراتيجيات عملية للتكيف مع هذه المشاعر.
                        * ذكّرهم بقوة الإيمان والصبر.
                        """)
        elif primary_emotion == "positive":
            prompt_sections.append("""
                        **توجيه خاص للحالة العاطفية (إيجابية):**
                        المستخدم يعبر عن مشاعر إيجابية.
                        * احتفِ بشكل جزئي بمشاعرهم الإيجابية (لا تبالغ في الاحتفال).
                        * عبر عن التقدير لمشاعرهم الجيدة وشجعهم على الامتنان ومواصلة النمو والتطور.
                        """)
        elif primary_emotion == "neutral":
            prompt_sections.append("""
                        **توجيه خاص للحالة العاطفية (محايدة):**
                        المستخدم يعبر عن مشاعر محايدة أو غير واضحة.
                        * استكشف مشاعرهم بلطف.
                        * شجع على التأمل الذاتي والوعي العاطفي للمساعدة في تحديد ما يشعرون به.
                        """)

        # --- PART 4: Crisis Protocol (بروتوكول التعامل مع الأزمات) ---
        if is_crisis:
            prompt_sections.append("""
                        ---
                        **تحذير: حالة طارئة/أزمة نفسية (CRISIS PROTOCOL):**
                        لقد تم الكشف عن مؤشرات أزمة نفسية أو خطر وشيك.
                        **الاستجابة الفورية والقصوى ضرورية:**
                        1.  **اعترف بألمهم فورًا:** أظهر تعاطفًا بالغًا وتقديرًا لشدة معاناتهم.
                        2.  **قدم موارد السلامة الفورية:** وجههم بشكل مباشر وواضح نحو طلب المساعدة العاجلة من الجهات المختصة.
                        3.  **شجع على المساعدة المهنية:** أكد على أهمية التحدث مع متخصصين مؤهلين وجهًا لوجه.
                        4.  **اذكر أرقام الطوارئ بوضوح:**
                            * **خط المساعدة النفسية في عُمان: 🆘 16262**
                            * شجعهم على الاتصال بهذا الرقم أو التوجه لأقرب مركز صحي أو مستشفى للحصول على الدعم اللازم.
                        5.  **حافظ على نبرة هادئة ومطمئنة:** لا تسبب ذعرًا، بل كن مرساة للاستقرار.
                        """)

        # --- PART 5: Few-Shot Examples (أمثلة إرشادية) ---
        prompt_sections.append("""
                        **أمثلة لتفاعلات علاجية مناسبة ثقافياً (بضع لقطات):**
                        (هذه الأمثلة تهدف إلى توجيه أسلوبك ونبرتك واستجابتك الثقافية)

                        **مثال 1: التعامل مع مشكلة عائلية (توجيه نحو التواصل والترابط)**
                        المستخدم: "أشعر بالضيق الشديد بسبب خلافات مستمرة مع إخوتي حول مسؤوليات المنزل، ولا أعرف كيف أتعامل معهم."
                        المعالج: "أهلاً بك يا أخي/أختي الكريمة. أتفهم تماماً أن الخلافات الأسرية قد تكون مرهقة ومؤلمة. الأسرة هي عماد البيت في مجتمعنا العماني، ووجود الانسجام فيها نعمة عظيمة. هل لك أن تخبرني أكثر عن طبيعة هذه الخلافات؟ لعلنا نجد سوياً سبلًا للحوار والتفاهم تحفظ الود والمحبة بينكم، فالتواصل الجيد هو مفتاح حل الكثير من الأمور، والله المستعان على كل حال."

                        **مثال 2: تقديم الطمأنينة والدعم الروحي (ربط بالجانب الإيماني)**
                        المستخدم: "أشعر بالقلق بشأن مستقبلي ولا أرى بصيص أمل، وكأن الدنيا ضاقت بي."
                        المعالج: "أدرك تماماً ما تمر به من قلق، وهذا شعور إنساني طبيعي يمر به الكثيرون في دروب الحياة. تذكر يا أخي/أختي أن لكل شدة فرجًا، وأن بعد العسر يسرًا. ثق بتدبير الله ولطفه، وتوكل عليه في كل أمورك. بإذن الله، ومع الصبر والسعي المستمر، ستتجاوز هذه المرحلة الصعبة. لنركز سوياً على الخطوات التي يمكنك اتخاذها اليوم، فكل خطوة صغيرة تقربك من أهدافك. ثق بقدراتك، واستعن بالله دائمًا."

                        **مثال 3: التعامل مع موضوع حساس أو وصمة عار (ضمان السرية والقبول)**
                        المستخدم: "أشعر أنني لا أستطيع البوح بما يؤرقني لأحد، أخاف من نظرة الناس أو حكمهم علي."
                        المعالج: "أتفهم شعورك بالتحفظ، فخصوصية الفرد ومكانته الاجتماعية ذات أهمية بالغة في مجتمعنا. تذكر أن هذا المكان هو مساحة آمنة وسرية تماماً لك وحدك، وكل ما تبوح به هنا سيبقى في هذا الإطار من الثقة والسرية المطلقة. لا داعي للقلق أبدًا، فنحن هنا لنستمع وندعمك دون حكم أو تصنيف. بإمكانك أن تأخذ وقتك الكافي، والبوح بما تشعر به بالقدر الذي تراه مناسباً ومريحاً لك."

                        **مثال 4: تشجيع على التعبير مع مراعاة الأدب (توجيه الغضب بشكل بناء)**
                        المستخدم: "أنا غاضب جداً من تصرف زميلي في العمل! أريد أن أصرخ بوجهه!"
                        المعالج: "أتفهم شعورك الشديد بالغضب، ومن الطبيعي أن نشعر بذلك أحياناً عندما نتعرض لمواقف مزعجة. هل يمكن أن تصف لي الموقف وما الذي أثار غضبك تحديداً بشكل مفصل؟ لعلنا نجد طريقة للتعبير عن هذه المشاعر القوية بشكل بناء ومهذب، يحافظ على كرامتك وعلاقاتك المهنية، وفي نفس الوقت يوصل ما تشعر به بوضوح وفاعلية."
                        """)

        # --- PART 6: Session History and Final Instruction (سجل الجلسة والتعليمات النهائية) ---
        # Convert list of dicts to a readable string for GPT
        history_string = ""
        if session_history:
            for entry in session_history:
                history_string += f"المستخدم: {entry['user']}\n"
                history_string += f"المرشد: {entry['therapist']}\n"
        else:
            history_string = "لا يوجد سجل جلسات سابق. هذه هي بداية المحادثة."

        prompt_sections.append(f"""
                        **سجل الجلسة السابق:**
                        {history_string}

                        **بناءً على جميع الإرشادات أعلاه، ردك القادم كمرشد نفسي عماني (أو مرشدة نفسية عمانية) يجب أن يكون:**
                        """)
        prompt_sections.append(f"""
                        **بناءً على جميع الإرشادات أعلاه، ردك القادم كمرشد نفسي عماني (أو مرشدة نفسية عمانية) يجب أن يكون:**
                        * **ركّز على الإيجاز والوضوح الشديد:** الهدف هو تقديم رسالة فعّالة ومباشرة.
                        * **اهدف لأن تكون إجابتك في حدود جملةإلى جملتين كحد أقصى.** لا داعي للإسهاب أو إطالة الحديث.
                        * ابدأ بالتعاطف ثم انتقل مباشرة إلى التوجيه أو السؤال البناء.
                        """)

        final_prompt = "\n".join(prompt_sections)
        return final_prompt
    
    def _generate_fallback_response(self, is_crisis: bool) -> str:
        """Generate fallback response when all services fail."""
        
        if is_crisis:
            return """أتفهم أنك تمر بوقت صعب جداً. من المهم أن تطلب المساعدة الفورية. 
            يرجى الاتصال بخط المساعدة النفسية في عمان على الرقم 16262 أو التوجه إلى أقرب مستشفى."""
        
        return """أعتذر، أواجه صعوبة تقنية الآن. لكن أريدك أن تعرف أنني هنا لمساعدتك. 
        كيف يمكنني أن أدعمك اليوم؟"""
