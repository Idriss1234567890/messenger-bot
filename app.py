from flask import Flask, request, jsonify

app = Flask(__name__)

# تحقق من التوكن (يجب استبداله بتوكنك الخاص)
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # تحقق من التوكن عند إعداد الويب هوك
    token = request.args.get('hub.verify_token')
    if token == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Verification failed"

@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    # استخراج الرسالة الواردة
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                # إرسال رد "مرحبًا"
                send_message(sender_id, "مرحبًا!")
    return jsonify({"status": "ok"})

def send_message(recipient_id, message):
    # استبدال "YOUR_PAGE_ACCESS_TOKEN" برمز الوصول الخاص بصفحتك
    access_token = "YOUR_PAGE_ACCESS_TOKEN"
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    import requests
    response = requests.post(url, json=data, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
