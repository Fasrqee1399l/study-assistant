import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# تهيئة عميل Gemini API باستخدام المفتاح المعتمد في المتغيرات البيئية
api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key) if api_key else None

# قاعدة بيانات الدروس والأسئلة والمستطيلات المقترحة
LESSONS_DATA = {
    "lesson1": {
        "title": "الدرس الأول: مدخل إلى علم الأحياء",
        "summary": """
        <h3>1. مفهوم علم الأحياء</h3>
        <p>يعنى بدراسة أنواع الحياة وطبيعتها وتركيب المخلوقات الحية ووظائفها وتفاعلها مع بعضها.</p>
        
        <h3>2. إسهامات العلماء</h3>
        <ul>
            <li><b>ابن سينا:</b> دراسة تنوع الحياة ووصف تراكيب النباتات والحيوانات.</li>
            <li><b>ابن البيطار:</b> كتاب (المغني في الأدوية المفردة) في العقاقير.</li>
            <li><b>أبو بكر الرازي:</b> اكتشاف الميكروبات ووصف الجدري والحصبة.</li>
            <li><b>تشارلز درو:</b> فصل بلازما الدم وإنشاء بنوك الدم.</li>
        </ul>

        <h3>3. خصائص المخلوقات الحية (8 خصائص)</h3>
        <ol>
            <li><b>مكون من خلية أو أكثر:</b> وحيدة الخلية (كالبكتيريا) أو عديدة الخلايا (كالإنسان).</li>
            <li><b>إظهار التنظيم (التعضي):</b> ذرات ⬅️ خلايا ⬅️ أنسجة ⬅️ أعضاء ⬅️ أجهزة ⬅️ جسم الكائن.</li>
            <li><b>النمو:</b> زيادة في كتلة الفرد وتكون تراكيب جديدة.</li>
            <li><b>التكاثر:</b> ضروري لحفظ النوع من الانقراض وليست شرطاً لبقاء الفرد نفسه.</li>
            <li><b>الحاجة إلى الطاقة:</b> ذاتية التغذية أو غير ذاتية التغذية.</li>
            <li><b>الاستجابة للمثيرات:</b> التفاعل مع التغيرات الداخلية والخارجية.</li>
            <li><b>الاتزان الداخلي:</b> تنظيم الظروف الداخلية للحفاظ على الحياة.</li>
            <li><b>التكيف:</b> صفات موروثة تساعد على ملاءمة البيئة للبقاء.</li>
        </ol>
        """,
        "questions": [
            {
                "id": 1,
                "text": "أي مما يلي يمثل الترتيب الصحيح لمستويات التنظيم في الكائنات عديدة الخلايا؟",
                "options": ["أعضاء -> أنسجة -> خلايا -> أجهزة", "خلايا -> أنسجة -> أعضاء -> أجهزة", "أنسجة -> خلايا -> أجهزة -> أعضاء"],
                "correct": 1,
                "explanation": "تتجمع الخلايا المتخصصة لتشكل أنسجة، والأنسجة تشكل أعضاء، والأعضاء تشكل أجهزة حيوية."
            },
            {
                "id": 2,
                "text": "العالم المسلم الذي اكتشف الميكروبات المسببة للمرض وهو أول من كتب وصفاً للجدري والحصبة هو:",
                "options": ["ابن سينا", "ابن البيطار", "أبو بكر الرازي"],
                "correct": 2,
                "explanation": "أبو بكر الرازي هو أول من اكتشف الميكروبات ووصف الجدري والحصبة بأسلوب علمي."
            },
            {
                "id": 3,
                "text": "الخاصية الحيوية التي تضمن بقاء النوع وحمايته من الانقراض هي:",
                "options": ["التكاثر", "الاتزان الداخلي", "الاستجابة للمثيرات"],
                "correct": 0,
                "explanation": "التكاثر يضمن استمرار النوع ومنع انقراضه ولكنه ليس شرطاً لبقاء الفرد بحد ذاته."
            }
        ],
        "ai_suggestions": [
            "اشرح لي فرق المفهوم بين المثير والاستجابة والتكيف بأمثلة واقعية من حياتنا.",
            "كيف تضمن خاصية الاتزان الداخلي بقاء جسم الكائن الحي عند التغير الشديد في البيئة؟",
            "اختبر قوة حفظي في هذا الدرس: اطرح عليّ سؤالاً تحليلياً وافحص إجابتي.",
            "ما هي أكثر النقاط والأخطاء الشائعة للطلاب في أسئلة اختبار هذا الدرس؟"
        ]
    },
    "lesson2": {
        "title": "الدرس الثاني: طبيعة العلم وطرائقه",
        "summary": """
        <h3>1. العلم الطبيعي (التجريبي)</h3>
        <p>بناء من المعرفة يعتمد على دراسة الطبيعة بالملاحظة والتجربة (مثل الفيزياء والكيمياء والأحياء)، بخلاف العلوم غير الطبيعية كالأدب والشعر.</p>

        <h3>2. خصائص العلم الطبيعي</h3>
        <ul>
            <li>يعتمد على الدليل والنظريات العلمية.</li>
            <li>يوسع المعرفة وينتج أسئلة جديدة للتطوير.</li>
            <li>يتحدى النظريات المقبولة بالنقاش العلمي.</li>
            <li>يخضع لمراجعة الأقران لضمان الدقة والموضوعية.</li>
            <li>يستخدم النظام المتري (SI) للقياس المعياري (متر، كيلوجرام، لتر، ثانية).</li>
        </ul>

        <h3>3. خطوات الطرائق العلمية</h3>
        <ol>
            <li><b>طرح السؤال والملاحظة:</b> جمع بيانات منظم يعقبه استنتاج منطقي.</li>
            <li><b>صياغة الفرضية:</b> تفسير قابل للاختبار والتجريب.</li>
            <li><b>إجراء التجربة المنضبطة:</b> تتكون من مجموعة ضابطة (للمقارنة) ومجموعة تجريبية.</li>
            <li><b>المتغيرات:</b> المستقل (العامل المُختَبَر) والمتغير التابع (النتيجة المترتبة عليه).</li>
            <li><b>تحليل البيانات وتسجيل الاستنتاجات:</b> قراءة الرسوم البيانية والجداول وإعلان النتائج.</li>
        </ol>
        """,
        "questions": [
            {
                "id": 1,
                "text": "العامل الذي يغيره الباحث عمداً في التجربة المنضبطة لمعرفة تأثيره يسمى:",
                "options": ["المتغير التابع", "المتغير المستقل", "المجموعة الضابطة"],
                "correct": 1,
                "explanation": "المتغير المستقل هو العامل الذي يتحكم فيه الباحث ليختبر مدى تأثيره في النتيجة."
            },
            {
                "id": 2,
                "text": "عملية فحص طرائق إجراء التجارب ودقة نتائجها من قِبل علماء مختصين قبل نشرها تسمى:",
                "options": ["مراجعة الأقران", "الأخلاق العلمية", "صياغة الفرضية"],
                "correct": 0,
                "explanation": "مراجعة الأقران تضمن الموثوقية والدقة العلمية قبل اعتماد النشر."
            },
            {
                "id": 3,
                "text": "أي وحدات النظام الدولي (SI) تُستخدم لقياس حجم السوائل؟",
                "options": ["المتر", "الكيلوجرام", "اللتر"],
                "correct": 2,
                "explanation": "اللتر هو الوحدة المعيارية المعتمدة لقياس الحجم في النظام المتري الدولي."
            }
        ],
        "ai_suggestions": [
            "ما الفرق بين الفرضية والنظرية العلمية؟ أعطني مثالاً بسيطاً لتوضيح الفرق.",
            "كيف أفرق بسهولة بين المتغير المستقل والمتغير التابع في أي تجربة تجيني بالامتحان؟",
            "اختبر قوة حفظي في خطوات الطريقة العلمية: اطرح عليّ سؤالاً تحليلياً وافحص إجابتي.",
            "ما هي التجميعات والأخطاء الشائعة للطلاب في أسئلة هذا الدرس؟"
        ]
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة أحياء التعليمية</title>
    <style>
        :root {
            --primary: #10b981;
            --primary-dark: #059669;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
        }

        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .container {
            max-width: 800px;
            width: 100%;
        }

        .nav-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .nav-btn {
            flex: 1;
            padding: 12px;
            border: 2px solid var(--primary);
            background: white;
            color: var(--primary-dark);
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.2s;
        }

        .nav-btn.active, .nav-btn:hover {
            background: var(--primary);
            color: white;
        }

        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
            border: 1px solid var(--border);
        }

        .section-title {
            color: var(--primary-dark);
            border-bottom: 2px solid var(--border);
            padding-bottom: 8px;
            margin-top: 0;
        }

        .ai-suggestions-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 15px;
        }

        .ai-card {
            background: #f0fdf4;
            border: 1px solid #a7f3d0;
            border-radius: 8px;
            padding: 14px;
            cursor: pointer;
            transition: 0.2s;
            font-weight: 500;
            font-size: 0.95rem;
        }

        .ai-card:hover {
            background: #dcfce7;
            transform: translateY(-2px);
        }

        .quiz-option {
            background: var(--bg);
            border: 1px solid var(--border);
            padding: 12px;
            border-radius: 6px;
            margin: 8px 0;
            cursor: pointer;
            transition: 0.2s;
        }

        .quiz-option:hover {
            background: #f1f5f9;
        }

        .explanation {
            display: none;
            padding: 10px;
            background: #eff6ff;
            border-right: 4px solid #3b82f6;
            margin-top: 8px;
            font-size: 0.9rem;
        }

        /* AI Floating Widget */
        .ai-fab {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
        }

        .ai-chat-window {
            display: none;
            position: fixed;
            bottom: 85px;
            left: 20px;
            width: 350px;
            height: 450px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
        }

        .chat-header {
            background: var(--primary);
            color: white;
            padding: 12px 16px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }

        .chat-messages {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .message {
            padding: 8px 12px;
            border-radius: 8px;
            max-width: 80%;
            font-size: 0.9rem;
        }

        .message.user {
            background: #e0e7ff;
            align-self: flex-end;
        }

        .message.bot {
            background: #f1f5f9;
            align-self: flex-start;
        }

        .chat-input-area {
            display: flex;
            border-top: 1px solid var(--border);
            padding: 8px;
        }

        .chat-input-area input {
            flex: 1;
            border: 1px solid var(--border);
            padding: 8px;
            border-radius: 4px;
            outline: none;
        }

        .chat-input-area button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 12px;
            margin-right: 4px;
            border-radius: 4px;
            cursor: pointer;
        }

        @media (max-width: 600px) {
            .ai-suggestions-grid { grid-template-columns: 1fr; }
            .ai-chat-window { width: 90%; left: 5%; }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="nav-buttons">
        <button class="nav-btn active" onclick="loadLesson('lesson1')">الدرس الأول</button>
        <button class="nav-btn" onclick="loadLesson('lesson2')">الدرس الثاني</button>
    </div>

    <!-- قسم الملخص -->
    <div class="card">
        <h2 class="section-title" id="lesson-title">--</h2>
        <div id="lesson-summary"></div>
    </div>

    <!-- قسم المستطيلات المقترحة للذكاء الاصطناعي -->
    <div class="card">
        <h3 class="section-title">أسئلة مقترحة للمساعد الذكي</h3>
        <p style="font-size: 0.9rem; color: #64748b;">اضغط على أي مستطيل للانتقال بالشات الفوري مع Ai:</p>
        <div class="ai-suggestions-grid" id="ai-suggestions"></div>
    </div>

    <!-- قسم زر بدء الاختبار والأسئلة -->
    <div class="card">
        <h3 class="section-title">الاختبار التفاعلي المجهز</h3>
        <button id="start-quiz-btn" class="nav-btn" onclick="toggleQuiz()" style="width: 100%;">بدء الاختبار التفاعلي</button>
        <div id="quiz-container" style="display: none; margin-top: 15px;"></div>
    </div>
</div>

<!-- AI Floating Widget -->
<button class="ai-fab" onclick="toggleChat()">Ai</button>

<div class="ai-chat-window" id="chat-window">
    <div class="chat-header">
        <span>المساعد الذكي</span>
        <span style="cursor:pointer;" onclick="toggleChat()">✕</span>
    </div>
    <div class="chat-messages" id="chat-messages">
        <div class="message bot">مرحباً بك! أنا مساعدك الذكي في مادة الأحياء. كيف يمكنني مساعدتك اليوم؟</div>
    </div>
    <div class="chat-input-area">
        <input type="text" id="chat-input" placeholder="اكتب سؤالك هنا..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">إرسال</button>
    </div>
</div>

<script>
    let currentLessonKey = 'lesson1';
    const lessonsData = {{ lessons_json | safe }};

    function loadLesson(key) {
        currentLessonKey = key;
        document.querySelectorAll('.nav-btn').forEach((btn, idx) => {
            if((key === 'lesson1' && idx === 0) || (key === 'lesson2' && idx === 1)) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        const lesson = lessonsData[key];
        document.getElementById('lesson-title').innerText = lesson.title;
        document.getElementById('lesson-summary').innerHTML = lesson.summary;

        // تحميل الاقتراحات
        const suggContainer = document.getElementById('ai-suggestions');
        suggContainer.innerHTML = '';
        lesson.ai_suggestions.forEach(text => {
            const card = document.createElement('div');
            card.className = 'ai-card';
            card.innerText = text;
            card.onclick = () => askAiDirectly(text);
            suggContainer.appendChild(card);
        });

        // إخفاء الاختبار عند التبديل
        document.getElementById('quiz-container').style.display = 'none';
        document.getElementById('start-quiz-btn').innerText = 'بدء الاختبار التفاعلي';
    }

    function toggleQuiz() {
        const container = document.getElementById('quiz-container');
        const btn = document.getElementById('start-quiz-btn');
        
        if (container.style.display === 'none') {
            renderQuiz();
            container.style.display = 'block';
            btn.innerText = 'إخفاء الاختبار';
        } else {
            container.style.display = 'none';
            btn.innerText = 'بدء الاختبار التفاعلي';
        }
    }

    function renderQuiz() {
        const container = document.getElementById('quiz-container');
        container.innerHTML = '';
        const questions = lessonsData[currentLessonKey].questions;

        questions.forEach((q, qIdx) => {
            const qDiv = document.createElement('div');
            qDiv.style.marginBottom = '20px';
            qDiv.innerHTML = `<strong>س${qIdx+1}: ${q.text}</strong>`;

            q.options.forEach((opt, optIdx) => {
                const optDiv = document.createElement('div');
                optDiv.className = 'quiz-option';
                optDiv.innerText = opt;
                optDiv.onclick = () => checkAnswer(qIdx, optIdx, q.correct, q.explanation, optDiv);
                qDiv.appendChild(optDiv);
            });

            const expDiv = document.createElement('div');
            expDiv.id = `exp-${qIdx}`;
            expDiv.className = 'explanation';
            qDiv.appendChild(expDiv);

            container.appendChild(qDiv);
        });
    }

    function checkAnswer(qIdx, selectedIdx, correctIdx, explanation, el) {
        const parent = el.parentElement;
        const options = parent.querySelectorAll('.quiz-option');
        options.forEach(opt => opt.style.pointerEvents = 'none');

        const expDiv = parent.querySelector('.explanation');
        
        if(selectedIdx === correctIdx) {
            el.style.background = '#dcfce7';
            el.style.borderColor = '#16a34a';
            expDiv.innerHTML = `<b>إجابة صحيحة!</b> ${explanation}`;
        } else {
            el.style.background = '#fee2e2';
            el.style.borderColor = '#dc2626';
            options[correctIdx].style.background = '#dcfce7';
            expDiv.innerHTML = `<b>إجابة خاطئة.</b> ${explanation}`;
        }
        expDiv.style.display = 'block';
    }

    function toggleChat() {
        const win = document.getElementById('chat-window');
        win.style.display = (win.style.display === 'flex') ? 'none' : 'flex';
    }

    function askAiDirectly(text) {
        const win = document.getElementById('chat-window');
        win.style.display = 'flex';
        document.getElementById('chat-input').value = text;
        sendMessage();
    }

    function sendMessage() {
        const input = document.getElementById('chat-input');
        const text = input.value.trim();
        if(!text) return;

        appendMessage(text, 'user');
        input.value = '';

        fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: text,
                lesson_key: currentLessonKey
            })
        })
        .then(res => res.json())
        .then(data => {
            appendMessage(data.response, 'bot');
        })
        .catch(() => {
            appendMessage("عذراً، حدث خطأ أثناء الاتصال بالذكاء الاصطناعي.", 'bot');
        });
    }

    function appendMessage(text, sender) {
        const msgs = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.innerText = text;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    }

    function handleKeyPress(e) {
        if(e.key === 'Enter') sendMessage();
    }

    // تشغيل الدرس الأول تلقائياً عند فتح الصفحة
    loadLesson('lesson1');
</script>

</body>
</html>
"""

@app.route('/')
def home():
    import json
    return render_template_string(HTML_TEMPLATE, lessons_json=json.dumps(LESSONS_DATA, ensure_ascii=False))

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json or {}
    user_msg = data.get('message', '')
    lesson_key = data.get('lesson_key', 'lesson1')
    
    lesson_info = LESSONS_DATA.get(lesson_key, {})
    lesson_title = lesson_info.get('title', '')
    lesson_summary = lesson_info.get('summary', '')

    system_prompt = f"""
    أنت معلم أحياء متكتم وذكي تجيب بأسلوب مبسط وشيق.
    سياق الدرس الحالي هو: {lesson_title}.
    ملخص محتوى الدرس: {lesson_summary}.
    أجب عن سؤال الطالب بناءً على محتوى هذا الدرس باختصار ودقة ودون استخدام إيموجيات.
    """

    if not client:
        return jsonify({"response": "لم يتم إعداد مفتاح API الخاص بـ Gemini بشكل صحيح."})

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{system_prompt}\n\nسؤال الطالب: {user_msg}"
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
