import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# إعداد العميل للتواصل مع نموذج Gemini
# يتم جلب المفتاح تلقائياً من بيئة العمل على Render (GEMINI_API_KEY)
client = genai.Client()

@app.route('/')
def home():
    # عرض صفحة index.html الموجودة داخل مجلد templates
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # إرسال الطلب إلى نموذج Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
