import os
import json
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# Apna asli blog URL yahan check kar lein
BLOG_URL = "https://technovexa.blogspot.com" 
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

def get_latest_post_url():
    """RSS Feed se latest post ka URL nikalne ke liye"""
    feed_url = f"{BLOG_URL}/feeds/posts/default?alt=rss"
    try:
        response = requests.get(feed_url, timeout=15)
        # Fix: 'status_status' ko badal kar 'status_code' kar diya gaya hai
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # RSS item se link nikalna
            item = root.find('.//item')
            if item is not None:
                latest_link = item.find('link').text
                return latest_link
    except Exception as e:
        print(f"❌ Feed loading error: {e}")
    return None

def trigger_indexing(url):
    """Google Indexing API ko request bhejne ke liye"""
    print(f"Starting Google Indexing for: {url}")
    try:
        if not SERVICE_ACCOUNT_JSON:
            print("❌ Error: GOOGLE_SERVICE_ACCOUNT_JSON Secret is missing!")
            return

        info = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ["https://www.googleapis.com/auth/indexing"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        service = build('indexing', 'v3', credentials=creds)
        
        body = {"url": url, "type": "URL_UPDATED"}
        result = service.urlNotifications().publish(body=body).execute()
        print(f"✅ Google Indexing request success for: {url}")
    except Exception as e:
        print(f"❌ Indexing API Error: {e}")

if __name__ == "__main__":
    latest_url = get_latest_post_url()
    
    # URL tracking file
    last_url_file = "last_indexed_url.txt"
    last_url = ""
    
    if os.path.exists(last_url_file):
        with open(last_url_file, "r") as f:
            last_url = f.read().strip()

    if latest_url and latest_url != last_url:
        trigger_indexing(latest_url)
        # Naya URL save karein taaki duplicate indexing na ho
        with open(last_url_file, "w") as f:
            f.write(latest_url)
    else:
        print("ℹ️ No new posts found or already indexed.")
