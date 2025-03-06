import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
import pytz
from feedgenerator import Rss201rev2Feed
import difflib

# Constants
SCRAPE_BUCKET = 'scrape-bucket'
FEEDS_DIR = 'feeds'
APPLE_RESOURCES_FILE = 'apple_resources_content.txt'
RSS_FILE = 'apple_resources_feed.xml'
URL = 'https://developer.apple.com/design/resources/'

def get_page_content():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text().strip()

def load_previous_content():
    file_path = os.path.join(SCRAPE_BUCKET, APPLE_RESOURCES_FILE)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_current_content(content):
    os.makedirs(SCRAPE_BUCKET, exist_ok=True)
    file_path = os.path.join(SCRAPE_BUCKET, APPLE_RESOURCES_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_changes(old_content, new_content):
    if not old_content:
        return "Initial scan of Apple Developer Resources page."
    
    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        lineterm='',
        n=0
    )
    changes = '\n'.join(list(diff)[2:])  # Skip the first two lines of diff output
    return changes if changes else "Content changed but no specific differences could be identified."

def update_rss(title, description):
    rss_path = os.path.join(FEEDS_DIR, RSS_FILE)
    current_time = datetime.datetime.now(pytz.UTC)
    
    if os.path.exists(rss_path):
        existing_feed = feedparser.parse(rss_path)
        feed = Rss201rev2Feed(
            title="Apple Developer Resources Monitor",
            link=URL,
            description="Monitoring changes to Apple Developer Resources page",
            language="en",
        )
        
        # Add existing items
        for item in existing_feed.entries:
            feed.add_item(
                title=item.title,
                link=item.link,
                description=item.description,
                pubdate=datetime.datetime(*item.published_parsed[:6], tzinfo=pytz.UTC),
                unique_id=item.get('id', item.link)
            )
    else:
        feed = Rss201rev2Feed(
            title="Apple Developer Resources Monitor",
            link=URL,
            description="Monitoring changes to Apple Developer Resources page",
            language="en",
        )

    # Add new item
    feed.add_item(
        title=title,
        link=URL,
        description=description,
        pubdate=current_time,
        unique_id=f"{URL}#{current_time.isoformat()}"
    )

    # Ensure the feeds directory exists
    os.makedirs(FEEDS_DIR, exist_ok=True)
    
    # Write the updated feed
    with open(rss_path, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')

def check_for_changes():
    current_content = get_page_content()
    previous_content = load_previous_content()
    
    if current_content != previous_content:
        title = "CHANGES DETECTED: Apple Developer Resources"
        changes = get_changes(previous_content, current_content)
        save_current_content(current_content)
    else:
        title = "NO CHANGES DETECTED: Apple Developer Resources"
        changes = "No changes detected in the latest scan."
    
    update_rss(title, changes)
    print(title)
    print(changes)

if __name__ == "__main__":
    check_for_changes()