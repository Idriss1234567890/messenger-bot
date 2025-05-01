from flask import Flask, request
import requests

app = Flask(__name__)

# قيم ثابتة مباشرة
VERIFY_TOKEN = "idriss123"  # ضع رمز التحقق الذي تختاره
PAGE_ACCESS_TOKEN = "EAATaVudqKO4BOZBtKh73Rq2L5BDoGFZAdCjN18bIoqyDxf90OOwsrDWpbro9ZCxuv6LBA7J6YMXW1QYDj8m20j60MWlPz42WoEs6fCwxnZAA6mTDwZA4taloBEBhbMwbOzwZCDIM6e1bUdTmmQ3EYu7ZBPZAT3rQk0jrhpmJzSVBlqrQrRVigB837ZBNufZBF212nHogZDZD"  # ضع التوكن الخاص بصفحتك هنا

@app.route('/')
def home():
    return 'Bot is running!'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verification token'
    
    elif request.method == 'POST':
        data = request.get_json()
        for entry in data.get("entry", []):
            for message_event in entry.get("messaging", []):
                sender_id = message_event["sender"]["id"]
                if "message" in message_event:
                    text = message_event["message"].get("text")
                    if text:
                        send_message(sender_id, "أهلاً! قلت: " + text)
        return "ok", 200

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, headers=headers, json=data)

if __name__ == '__main__':
    app.run()