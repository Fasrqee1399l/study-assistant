import os
import time
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# تهيئة عميل جوجل ذكاء اصطناعي
client = genai.Client()

SYSTEM_INSTRUCTION = (
    "أنت مساعد دراسي ذكي ومتخصص في مادة الأحياء للصف الأول الثانوي. "
    "عند طلب شرح أو تلخيص أي نقطة، قدم إجابات وافية وشاملة ومفصلة بأسلوب سهل ومبسط يناسب الطلاب."
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'الرجاء كتابة سؤال'}), 400

        # آلية إعادة المحاولة تلقائياً (3 مرات) عند وجود ضغط على السيرفر (503)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=f"{SYSTEM_INSTRUCTION}\n\nسؤال الطالب: {user_message}",
                )
                return jsonify({'response': response.text})

            except Exception as err:
                err_str = str(err)
                # إذا كان الخطأ بسبب ضغط الخوادم (503) ولم نتجاوز عدد المحاولات
                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                    time.sleep(2)  # الانتظار ثانيتين ثم إعادة المحاولة
                    continue
                else:
                    # إذا استمرت المشكلة يتم إظهار رسالة توضيحية بدل الخطأ البشع
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        return jsonify({'response': '⚠️ خوادم الذكاء الاصطناعي تشهد ضغطاً حالياً، يرجى الضغط على إرسال مرة أخرى بعد بضع ثوانٍ.'})
                    return jsonify({'response': f'حدث خطأ غير متوقع: {err_str}'})

    except Exception as e:
        return jsonify({'response': 'تعذر معالجة الطلب حالياً، حاول مجدداً.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
