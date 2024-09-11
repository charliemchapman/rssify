import json
import os
import feedparser
from feedgenerator import Rss201rev2Feed, Enclosure
import datetime
import pytz

# Define the directory for storing JSON files
SCRAPE_BUCKET = 'scrape-bucket'
FEEDS_DIR = 'feeds'
RSS_FILE = 'webster_kirwood_times_feed.xml'

def load_articles():
    file_path = os.path.join(SCRAPE_BUCKET, 'scraped_articles.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def load_posted_articles():
    file_path = os.path.join(SCRAPE_BUCKET, 'posted_articles.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_posted_articles(posted_articles):
    file_path = os.path.join(SCRAPE_BUCKET, 'posted_articles.json')
    with open(file_path, 'w') as f:
        json.dump(posted_articles, f)

def update_rss(new_articles):
    rss_path = os.path.join(FEEDS_DIR, RSS_FILE)
    
    if os.path.exists(rss_path):
        # Parse existing feed
        existing_feed = feedparser.parse(rss_path)
        
        # Create new feed with existing metadata
        feed = Rss201rev2Feed(
            title=existing_feed.feed.title,
            link=existing_feed.feed.link,
            description=existing_feed.feed.description,
            language=existing_feed.feed.language,
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
        # Create new feed if it doesn't exist
        feed = Rss201rev2Feed(
            title="Webster Kirwood Times",
            link="https://www.timesnewspapers.com/",
            description="Latest news from our Webster Kirwood Times",
            language="en",
        )
    
    # Add new articles
    current_time = datetime.datetime.now(pytz.UTC)
    for article in new_articles:
        feed.add_item(
            title=article['title'],
            link=article['link'],
            description=article['summary'],
            pubdate=current_time,
            unique_id=article['link'],
            enclosure=Enclosure(
                url=article['image_url'],
                length='0',
                mime_type='image/jpeg'
            ) if article['image_url'] else None
        )
    
    # Ensure the feeds directory exists
    os.makedirs(FEEDS_DIR, exist_ok=True)
    
    # Write the updated feed
    with open(rss_path, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')

def post_articles(num_articles=5):
    # Ensure the scrape-bucket directory exists
    os.makedirs(SCRAPE_BUCKET, exist_ok=True)

    all_articles = load_articles()
    posted_articles = load_posted_articles()
    
    # Find articles that haven't been posted yet
    new_articles = [a for a in all_articles if a['link'] not in posted_articles]
    
    # Sort articles by date (oldest first) and select the oldest num_articles
    articles_to_post = sorted(new_articles, key=lambda x: x['date'] or datetime.datetime.max.isoformat())[:num_articles]
    
    if articles_to_post:
        update_rss(articles_to_post)
        
        # Update the list of posted articles
        posted_articles.extend([a['link'] for a in articles_to_post])
        save_posted_articles(posted_articles)
        
        print(f"Posted {len(articles_to_post)} new articles")
    else:
        print("No new articles to post")

if __name__ == "__main__":
    post_articles()