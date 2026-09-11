import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

client = genai.Client()

SYSTEM_INSTRUCTION = (
    "أنت مساعد دراسي ذكي ومتخصص في مادة الأحياء. عند طلب شرح أو تلخيص أي نقطة، "
    "قدم إجابات وافية وشاملة ومفصلة بأسلوب سهل يناسب طلاب الثانوية."
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
            return jsonify({'error': 'Message is required'}), 400

        # استخدام النموذج المحدث gemini-3.6-flash
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=f"{SYSTEM_INSTRUCTION}\n\nسؤال الطالب: {user_message}",
        )

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
