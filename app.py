import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# استدعاء مفتاح API الخاص بـ Groq
client = Groq(api_key=os.environ.get("OPENAI_API_KEY"))

PREDEFINED_LESSONS = {
    "lesson1": {
        "title": "الدرس الأول: مقدمة في الذكاء الاصطناعي",
        "content": "الذكاء الاصطناعي هو فرع من علوم الحاسب يهدف إلى إنشاء أنظمة قادرة على محاكاة الذكاء البشري، مثل التعلم، والتفكير، وحل المشكلات."
    },
    "lesson2": {
        "title": "الدرس الثاني: قوانين نيوتن للحركة",
        "content": "تنص قوانين نيوتن للحركة على ثلاثة مبادئ أساسية: القانون الأول ينص على أن الجسم الساكن يبقى ساكناً والمتحرك يبقى متحركاً ما لم تؤثر عليه قوة خارجية."
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>المساعد الدراسي الذكي - أولمبياد ابتكار</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; text-align: right; }
        .container { max-width: 850px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        h1 { color: #1a365d; text-align: center; }
        p.subtitle { text-align: center; color: #4a5568; font-weight: bold; }
        select, textarea { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
        textarea { height: 120px; }
        button { background-color: #3182ce; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; font-weight: bold; }
        .chat-btn { background-color: #38a169; }
        .result-section { margin-top: 25px; background: #ebf8ff; padding: 20px; border-radius: 8px; border-right: 5px solid #3182ce; display: none; }
        .chat-section { margin-top: 20px; background: #f7fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; display: none; }
        .chat-history { max-height: 200px; overflow-y: auto; background: white; padding: 10px; border-radius: 6px; margin-bottom: 10px; }
        .chat-msg { margin: 5px 0; padding: 8px; border-radius: 6px; }
        .chat-user { background: #e2e8f0; }
        .chat-ai { background: #e6fffa; color: #234e52; }
        .loading { text-align: center; display: none; margin-top: 15px; color: #dd6b20; font-weight: bold; }
        pre { white-space: pre-wrap; font-family: inherit; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 المساعد الدراسي الذكي</h1>
        <p class="subtitle">منصة المذاكرة التفاعلية - أولمبياد ابتكار</p>
        
        <label>اختر الدرس المراد مذاكرته:</label>
        <select id="lessonSelect" onchange="handleLessonChange()">
            <option value="lesson1">الدرس الأول: مقدمة في الذكاء الاصطناعي</option>
            <option value="lesson2">الدرس الثاني: قوانين نيوتن للحركة</option>
            <option value="custom">أدخل درسًا آخر من عندك...</option>
        </select>

        <div id="customTextDiv" style="display: none; margin-top: 10px;">
            <label>نص الدرس الخاص بك:</label>
            <textarea id="customText" placeholder="انسخ نص الدرس هنا..."></textarea>
        </div>
        
        <button onclick="analyzeLesson()">بدء التلخيص وتوليد الأسئلة ✨</button>
        
        <div id="loading" class="loading">جاري تحليل الدرس وإعداد التلخيص والأسئلة التفاعلية... ⏳</div>
        
        <div id="resultSection" class="result-section">
            <h3>📌 الملخص والأسئلة التفاعلية:</h3>
            <pre id="resultContent"></pre>
            <button class="chat-btn" onclick="toggleChat()">💬 لديك استفسار؟ تحدث مع المساعد الذكي حول هذا الدرس</button>
        </div>

        <div id="chatSection" class="chat-section">
            <h4>💬 اسأل المساعد الذكي عن الدرس:</h4>
            <div id="chatHistory" class="chat-history"></div>
            <textarea id="chatInput" style="height: 60px;" placeholder="اكتب سؤالك هنا..."></textarea>
            <button onclick="sendChatMessage()">إرسال السؤال</button>
        </div>
    </div>

    <script>
        let currentLessonText = "";

        function handleLessonChange() {
            const select = document.getElementById('lessonSelect');
            document.getElementById('customTextDiv').style.display = select.value === 'custom' ? 'block' : 'none';
        }

        async function analyzeLesson() {
            const selectValue = document.getElementById('lessonSelect').value;
            const customText = document.getElementById('customText').value;
            const loading = document.getElementById('loading');
            const resultSection = document.getElementById('resultSection');

            loading.style.display = 'block';
            resultSection.style.display = 'none';

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lesson_key: selectValue, custom_text: customText })
                });

                const data = await response.json();
                loading.style.display = 'none';

                if (data.error) {
                    alert('خطأ: ' + data.error);
                } else {
                    currentLessonText = data.lesson_content;
                    document.getElementById('resultContent').textContent = data.result;
                    resultSection.style.display = 'block';
                }
            } catch (err) {
                loading.style.display = 'none';
                alert('حدث خطأ أثناء الاتصال بالسيرفر!');
            }
        }

        function toggleChat() {
            const chatSec = document.getElementById('chatSection');
            chatSec.style.display = chatSec.style.display === 'none' ? 'block' : 'none';
        }

        async function sendChatMessage() {
            const chatInput = document.getElementById('chatInput');
            const chatHistory = document.getElementById('chatHistory');
            const question = chatInput.value.trim();

            if (!question) return;

            chatHistory.innerHTML += `<div class="chat-msg chat-user"><strong>أنت:</strong> ${question}</div>`;
            chatInput.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lesson_content: currentLessonText, question: question })
                });

                const data = await response.json();
                if (data.reply) {
                    chatHistory.innerHTML += `<div class="chat-msg chat-ai"><strong>المساعد الذكي:</strong> ${data.reply}</div>`;
                }
            } catch (err) {
                alert('فشل إرسال السؤال');
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
    lesson_key = data.get('lesson_key', '')
    custom_text = data.get('custom_text', '')

    if lesson_key in PREDEFINED_LESSONS:
        lesson_text = PREDEFINED_LESSONS[lesson_key]["content"]
    elif lesson_key == 'custom' and custom_text:
        lesson_text = custom_text
    else:
        return jsonify({'error': 'يرجى اختيار درس أو كتابة نص الدرس'}), 400

    prompt = f"قم بتلخيص الدرس التالي واستخراج أهم المفاهيم وطرح 3 أسئلة تفاعلية هامة:\n{lesson_text}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({'result': response.choices[0].message.content, 'lesson_content': lesson_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    lesson_content = data.get('lesson_content', '')
    question = data.get('question', '')

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"بناء على الدرس: {lesson_content}\nأجب على سؤال الطالب: {question}"}]
        )
        return jsonify({'reply': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
