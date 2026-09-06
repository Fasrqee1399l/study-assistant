import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# استدعاء مفتاح API من إعدادات البيئة في Render
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# تصميم واجهة الموقع (HTML/CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>المساعد الدراسي الذكي - أولمبياد إبداء</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; text-align: right; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        p.subtitle { text-align: center; color: #7f8c8d; margin-bottom: 30px; }
        textarea { width: 100%; height: 150px; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        button { background-color: #3498db; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; font-weight: bold; }
        button:hover { background-color: #2980b9; }
        .result-box { margin-top: 30px; background: #eef7fc; padding: 20px; border-radius: 8px; border-right: 5px solid #3498db; display: none; }
        .loading { text-align: center; display: none; margin-top: 15px; color: #e67e22; font-weight: bold; }
        pre { white-space: pre-wrap; font-family: inherit; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 المساعد الدراسي الذكي</h1>
        <p class="subtitle">مشروع مخصص لأولمبياد إبداء - تلخيص المناهج وإنشاء أسئلة تفاعلية</p>
        
        <label for="lessonText"><strong>أدخل نص الدرس أو المنهج هنا:</strong></label>
        <textarea id="lessonText" placeholder="انسخ نص الدرس أو الفقرة واكودها هنا..."></textarea>
        
        <button onclick="processLesson()">تحليل الدرس والتلخيص والأسئلة ✨</button>
        
        <div id="loading" class="loading">جاري تحليل النص بواسطة الذكاء الاصطناعي... انتظر لحظة ⏳</div>
        
        <div id="resultBox" class="result-box">
            <h3>📌 النتائج:</h3>
            <pre id="resultContent"></pre>
        </div>
    </div>

    <script>
        async function processLesson() {
            const text = document.getElementById('lessonText').value;
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('resultBox');
            const resultContent = document.getElementById('resultContent');

            if (!text.trim()) {
                alert('الرجاء إدخال نص الدرس أولاً!');
                return;
            }

            loading.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });

                const data = await response.json();
                loading.style.display = 'none';

                if (data.error) {
                    alert('حدث خطأ: ' + data.error);
                } else {
                    resultContent.textContent = data.result;
                    resultBox.style.display = 'block';
                }
            } catch (err) {
                loading.style.display = 'none';
                alert('فشل الاتصال بالسيرفر!');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    user_text = data.get('text', '')

    if not user_text:
        return jsonify({'error': 'لم يتم تقديم أي نص'}), 400

    prompt = f"""
    أنت مساعد دراسي ذكي للطلاب. قم بتحليل النص التالي واعمل التالي:
    1. ملخص شامل للدرس في نقاط واضحة ومبسطة.
    2. استخراج الأفكار الرئيسية.
    3. إنشاء 3 أسئلة تفاعلية (اختيار من متعدد) مع ذكر الإجابة الصحيحة لكل سؤال.

    النص:
    {user_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت معلم ومساعد دراسي متخصص."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        result_text = response.choices[0].message.content
        return jsonify({'result': result_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
