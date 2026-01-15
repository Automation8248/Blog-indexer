import os
import json
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
BLOG_URL = "https://technovexa.blogspot.com" 
BLOG_NAME = "Technovexa" # Aapke blog ka naam
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Telegram par message bhejne ke liye"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram error: {e}")

def get_latest_post_url():
    feed_url = f"{BLOG_URL}/feeds/posts/default?alt=rss"
    try:
        response = requests.get(feed_url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            item = root.find('.//item')
            if item is not None:
                return item.find('link').text
    except Exception as e:
        print(f"❌ Feed error: {e}")
    return None

def trigger_indexing(url):
    print(f"Indexing request for: {url}")
    try:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ["https://www.googleapis.com/auth/indexing"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        service = build('indexing', 'v3', credentials=creds)
        
        body = {"url": url, "type": "URL_UPDATED"}
        service.urlNotifications().publish(body=body).execute()
        
        # Success Message for Telegram
        msg = f"<b>🚀 {BLOG_NAME} Indexing Update</b>\n\n✅ Successfully Indexed:\n{url}"
        send_telegram_message(msg)
        print("✅ Google Indexing success!")
    except Exception as e:
        print(f"❌ Indexing Error: {e}")

if __name__ == "__main__":
    latest_url = get_latest_post_url()
    last_url_file = "last_indexed_url.txt"
    last_url = ""
    
    if os.path.exists(last_url_file):
        with open(last_url_file, "r") as f:
            last_url = f.read().strip()

    if latest_url and latest_url != last_url:
        trigger_indexing(latest_url)
        with open(last_url_file, "w") as f:
            f.write(latest_url)
    else:
        print("ℹ️ No new posts or already indexed.")
