import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# استدعاء مفتاح API الخاص بـ Groq
client = Groq(api_key=os.environ.get("OPENAI_API_KEY"))

PREDEFINED_LESSONS = {
    "lesson1": {
        "title": "الدرس الأول: مقدمة في الذكاء الاصطناعي",
        "content": "الذكاء الاصطناعي هو فرع من علوم الحاسب يهدف إلى إنشاء أنظمة قادرة على محاكاة الذكاء البشري، مثل التعلم، والتفكير، وحل المشكلات. يتكون الذكاء الاصطناعي من مجالات فرعية مثل التعلم الآلي والتعلم العميق ورؤية الحاسوب ومعالجة اللغة الطبيعية."
    },
    "lesson2": {
        "title": "الدرس الثاني: قوانين نيوتن للحركة",
        "content": "تنص قوانين نيوتن للحركة على ثلاثة مبادئ أساسية: القانون الأول ينص على أن الجسم الساكن يبقى ساكناً والمتحرك يبقى متحركاً ما لم تؤثر عليه قوة خارجية. القانون الثاني يربط بين القوة والكتلة والتسارع (القوة = الكتلة × التسارع). القانون الثالث ينص على أن لكل فعل رد فعل مساوٍ له في المقدار ومضاد له في الاتجاه."
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
        h1 { color: #1a365d; text-align: center; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #4a5568; margin-bottom: 25px; font-weight: bold; }
        label { font-weight: bold; color: #2d3748; display: block; margin-top: 15px; margin-bottom: 5px; }
        select, textarea { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
        textarea { height: 120px; }
        button { background-color: #3182ce; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; font-weight: bold; transition: 0.2s; }
        button:hover { background-color: #2b6cb0; }
        .chat-btn { background-color: #38a169; margin-top: 10px; }
        .chat-btn:hover { background-color: #2f855a; }
        .result-section { margin-top: 25px; background: #ebf8ff; padding: 20px; border-radius: 8px; border-right: 5px solid #3182ce; display: none; }
        .chat-section { margin-top: 20px; background: #f7fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; display: none; }
        .chat-history { max-height: 200px; overflow-y: auto; background: white; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
        .chat-msg { margin: 5px 0; padding: 8px; border-radius: 6px; }
        .chat-user { background: #e2e8f0; text-align: right; }
        .chat-ai { background: #e6fffa; text-align: right; color: #234e52; }
        .loading { text-align: center; display: none; margin-top: 15px; color: #dd6b20; font-weight: bold; }
        pre { white-space: pre-wrap; font-family: inherit; line-height: 1.6; color: #2d3748; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 المساعد الدراسي الذكي</h1>
        <p class="subtitle">منصة المذاكرة التفاعلية - أولمبياد ابتكار</p>
        
        <label for="lessonSelect">اختر الدرس المراد مذاكرته:</label>
        <select id="lessonSelect" onchange="handleLessonChange()">
            <option value="lesson1">الدرس الأول: مقدمة في الذكاء الاصطناعي</option>
            <option value="lesson2">الدرس الثاني: قوانين نيوتن للحركة</option>
            <option value="custom">أدخل درسًا آخر من عندك...</option>
        </select>

        <div id="customTextDiv" style="display: none;">
            <label for="customText">نص الدرس الخاص بك:</label>
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
            <textarea id="chatInput" style="height: 60px;" placeholder="اكتب سؤالك هنا إذا لم تفهم جزءاً معنياً..."></textarea>
            <button onclick="sendChatMessage()">إرسال السؤال</button>
        </div>
    </div>

    <script>
        let currentLessonText = "";

        function handleLessonChange() {
            const select = document.getElementById('lessonSelect');
            const customDiv = document.getElementById('customTextDiv');
            if (select.value === 'custom') {
                customDiv.style.display = 'block';
            } else {
                customDiv.style.display = 'none';
            }
        }

        async function analyzeLesson() {
            const selectValue = document.getElementById('lessonSelect').value;
            const customText = document.getElementById('customText').value;
            const loading = document.getElementById('loading');
            const resultSection = document.getElementById('resultSection');
            const resultContent = document.getElementById('resultContent');

            loading.style.display = 'block';
            resultSection.style.display = 'none';
            document.getElementById('chatSection').style.display = 'none';

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
                    resultContent.textContent = data.result;
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
            chatHistory.scrollTop = chatHistory.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lesson_content: currentLessonText, question: question })
                });

                const data = await response.json();
                if (data.reply) {
                    chatHistory.innerHTML += `<div class="chat-msg chat-ai"><strong>المساعد الذكي:</strong> ${data.reply}</div>`;
                } else {
                    chatHistory.innerHTML += `<div class="chat-msg chat-ai"><strong>المساعد الذكي:</strong> حدث خطأ في الحصول على إجابة.</div>`;
                }
                chatHistory.scrollTop = chatHistory.scrollHeight;
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
        lesson_title = PREDEFINED_LESSONS[lesson_key]["title"]
    elif lesson_key == 'custom' and custom_text:
        lesson_text = custom_text
        lesson_title = "درس مخصص"
    else:
        return jsonify({'error': 'يرجى اختيار درس أو كتابة نص الدرس'}), 400

    prompt = f"""
    أنت معلم ومساعد دراسي ذكي. قم بتحليل الدرس التالي ({lesson_title}):

    1. **التلخيص الشامل:** قم بتلخيص أهم نقاط الدرس بشكل ملخص وواضح يسهل على الطالب استيعابه.
    2. **الأفكار الرئيسية:** اذكر أهم 3 مفاهيم في الدرس.
    3. **الأسئلة التفاعلية (حسب الأهمية):** صمم 3 أسئلة اختيار من متعدد هامة ومترتبة حسب الأهمية الاختيارية، واكتب الإجابة الصحيحة وشرح بسيط لها.

    نص الدرس:
    {lesson_text}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "أنت معلم دراسي متخصص ومساعد ذكي للطلاب."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        result_text = response.choices[0].message.content
        return jsonify({'result': result_text, 'lesson_content': lesson_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    lesson_content = data.get('lesson_content', '')
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'السؤال فارغ'}), 400

    prompt = f"""
    بناءً على الدرس التالي:
    "{lesson_content}"

    أجب عن سؤال الطالب التالي بأسلوب مبسط وواضح ومساعد:
    سؤال الطالب: {question}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "أنت معلم ودود يجيب على استفسارات الطلاب بأسلوب واضح وشائق."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
