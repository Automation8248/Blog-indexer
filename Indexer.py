import os
import json
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURATION
# Apna blog URL yahan dalein (e.g., https://technovexa.blogspot.com)
BLOG_URL = "https://technovexa.blogspot.com" 
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

def get_latest_post_url():
    """RSS Feed se latest post ka URL nikalne ke liye"""
    feed_url = f"{BLOG_URL}/feeds/posts/default?alt=rss"
    response = requests.get(feed_url)
    if response.status_status == 200:
        root = ET.fromstring(response.content)
        # Latest item ka link uthana
        latest_link = root.find('.//item/link').text
        return latest_link
    return None

def trigger_indexing(url):
    """Google Indexing API ko request bhejne ke liye"""
    print(f"Checking indexing for: {url}")
    try:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ["https://www.googleapis.com/auth/indexing"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        service = build('indexing', 'v3', credentials=creds)
        
        body = {"url": url, "type": "URL_UPDATED"}
        service.urlNotifications().publish(body=body).execute()
        print(f"✅ Google Indexing request sent for: {url}")
    except Exception as e:
        print(f"❌ Indexing Error: {e}")

if __name__ == "__main__":
    latest_url = get_latest_post_url()
    if latest_url:
        trigger_indexing(latest_url)
    else:
        print("No post found in feed.")
