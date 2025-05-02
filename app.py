from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import re
import threading
import time

app = Flask(__name__)

VERIFY_TOKEN = "idriss123"
PAGE_ACCESS_TOKEN = "EAATaVudqKO4BOZBtKh73Rq2L5BDoGFZAdCjN18bIoqyDxf90OOwsrDWpbro9ZCxuv6LBA7J6YMXW1QYDj8m20j60MWlPz42WoEs6fCwxnZAA6mTDwZA4taloBEBhbMwbOzwZCDIM6e1bUdTmmQ3EYu7ZBPZAT3rQk0jrhpmJzSVBlqrQrRVigB837ZBNufZBF212nHogZDZD"

user_sessions = {}

@app.route('/')
def home():
    return 'Manga bot is running!'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verification token'

    data = request.get_json()
    for entry in data.get("entry", []):
        for message_event in entry.get("messaging", []):
            sender_id = message_event["sender"]["id"]
            if "message" in message_event:
                text = message_event["message"].get("text")
                if text:
                    handle_message(sender_id, text.strip())
    return "ok", 200

def handle_message(sender_id, text):
    session = user_sessions.get(sender_id, {})

    if 'awaiting_chapter' in session:
        chapter = text
        manga_url = session['manga_url']
        del session['awaiting_chapter']
        threading.Thread(target=send_chapter_images, args=(sender_id, manga_url, chapter)).start()
        send_message(sender_id, f"جاري تحميل الفصل {chapter}...")
        return

    search_url = f"https://manga4life.com/search/?title={text.replace(' ', '%20')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', class_='seriesName')

    if not results:
        send_message(sender_id, "لم يتم العثور على مانجا بهذا الاسم.")
        return

    first_result = results[0]
    manga_title = first_result.text.strip()
    manga_link = 'https://manga4life.com' + first_result['href']

    user_sessions[sender_id] = {'manga_url': manga_link, 'awaiting_chapter': True}
    send_message(sender_id, f"تم العثور على: {manga_title}\nأرسل رقم الفصل الذي تريده.")

def send_chapter_images(sender_id, manga_url, chapter_num):
    manga_slug = manga_url.split('/')[-1]
    chapter_slug = f"{manga_slug}-chapter-{chapter_num}"
    chapter_url = f"https://manga4life.com/read-online/{chapter_slug}.html"

    response = requests.get(chapter_url)
    if response.status_code != 200:
        send_message(sender_id, "لم أتمكن من تحميل الفصل. تأكد من الرقم.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', text=re.compile('var _load_pages'))
    if not script_tag:
        send_message(sender_id, "لم يتم العثور على صفحات.")
        return

    matches = re.findall(r'"u":"(.*?)"', script_tag.string)
    if not matches:
        send_message(sender_id, "لا توجد صور في هذا الفصل.")
        return

    base_url = "https://img.mghubcdn.com/file/imghub/"
    for img in matches:
        image_url = base_url + img.replace('\\', '')
        send_image(sender_id, image_url)
        time.sleep(1.5)

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, headers=headers, json=data)

def send_image(recipient_id, image_url):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": False}
            }
        }
    }
    requests.post(url, params=params, headers=headers, json=data)

if __name__ == '__main__':
    app.run()
