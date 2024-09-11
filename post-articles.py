import json
import os
import feedgenerator
import datetime

# Define the directory for storing JSON files
SCRAPE_BUCKET = 'scrape-bucket'

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

def generate_rss(articles):
    feed = feedgenerator.Rss201rev2Feed(
        title="Webster Kirwood Times",
        link="https://www.timesnewspapers.com/",
        description="Latest news from our Webster Kirwood Times",
        language="en",
    )
    
    current_time = datetime.datetime.now(datetime.timezone.utc)
    
    for article in articles:
        item = {
            'title': article['title'],
            'link': article['link'],
            'description': article['summary'],
            'pubdate': current_time,  # Use current time for all articles
        }
        if article['image_url']:
            item['enclosure'] = feedgenerator.Enclosure(
                url=article['image_url'],
                length='0',
                mime_type='image/jpeg'
            )
        feed.add_item(**item)
    
    return feed.writeString('utf-8')

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
        rss_feed = generate_rss(articles_to_post)
        
        # Save the RSS feed
        feeds_dir = 'feeds'
        os.makedirs(feeds_dir, exist_ok=True)
        file_path = os.path.join(feeds_dir, 'webster_kirwood_times_feed.xml')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        
        # Update the list of posted articles
        posted_articles.extend([a['link'] for a in articles_to_post])
        save_posted_articles(posted_articles)
        
        print(f"Posted {len(articles_to_post)} new articles")
    else:
        print("No new articles to post")

if __name__ == "__main__":
    post_articles()