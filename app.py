import os
import time
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# تهيئة عميل جوجل للذكاء الاصطناعي
client = genai.Client()

SYSTEM_INSTRUCTION = (
    "أنت مساعد دراسي ذكي ومباشر لطلاب الصف الأول الثانوي في مادة الأحياء.\n"
    "التزم بالتعليمات الصارمة التالية أثناء الإجابة:\n"
    "1. أجب بشكل مختصر جداً ومباشر ودقيق علمياً بدون مقدمات أو خاتمة.\n"
    "2. عند طلب الفرق بين مفاهيم، قدم الفرق فقط في أسطر قصيرة ونقاط محددة ورؤوس أقلام واضحة.\n"
    "3. يمنع منعاً باتاً كتابة فقرات طويلة أو سرد أمثلة إلا إذا طلب الطالب مثالاً صراحة.\n"
    "4. لا تستخدم رموزاً رياضية أو لغة LaTeX، واستخدم لغة عربية سلسة وواضحة.\n"
    "5. تذكر محادثاتك السابقة مع الطالب للتجاوب مع استفساراته المباشرة."
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        messages_history = data.get('history', [])

        if not messages_history:
            return jsonify({'error': 'الرجاء كتابة سؤال'}), 400

        formatted_contents = [{"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION}]}]
        formatted_contents.extend(messages_history)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=formatted_contents
                )
                return jsonify({'response': response.text})

            except Exception as err:
                err_str = str(err)
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return jsonify({'response': 'تعذر الاتصال بالذكاء الاصطناعي، يرجى المحاولة مرة أخرى.'})

    except Exception as e:
        return jsonify({'response': 'تعذر معالجة الطلب حالياً.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
