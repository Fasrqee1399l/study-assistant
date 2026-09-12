import os
import time
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# تهيئة عميل جوجل للذكاء الاصطناعي
client = genai.Client()

SYSTEM_INSTRUCTION = (
    "أنت مساعد دراسي ذكي ومباشر لطلاب الصف الأول الثانوي في مادة الأحياء.\n"
    "التزم بالتعليمات الصارمة التالية:\n"
    "1. أجب عن سؤال الطالب فقط وبشكل مختصر ومباشر دون شرح الدرس كاملاً ودون إعطاء تلخيص إلا إذا طلب ذلك.\n"
    "2. لا تقدم أي أمثلة من الواقع أو البيئة إلا إذا طلب الطالب منك صراحة إعطاء مثال.\n"
    "3. لا تستخدم أية رموز رياضية أو لغات تنسيق غريبة مثل LaTeX أو أسهم المعادلات. اكتب بلغة عربية سلسة وواضحة فقط.\n"
    "4. تذكر دائماً أجزاء المحادثة السابقة لتجيب بذكاء ودقة إذا طلب الطالب إعادة الشرح أو الاستفسار عن نقطة سابقة."
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
                # استخدام النموذج المستقر لمنع أخطاء الأسماء
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=formatted_contents
                )
                return jsonify({'response': response.text})

            except Exception as err:
                err_str = str(err)
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        return jsonify({'response': '⚠️ الخادم مشغول حالياً، يرجى إعادة المحاولة بعد ثوانٍ.'})
                    return jsonify({'response': f'حدث خطأ في النظام: {err_str}'})

    except Exception as e:
        return jsonify({'response': 'تعذر معالجة الطلب حالياً.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
