import requests
from bs4 import BeautifulSoup
import datetime
import json
import os

def get_image_url(img_elem):
    # ... (keep this function as is)

def load_existing_articles():
    if os.path.exists('scraped_articles.json'):
        with open('scraped_articles.json', 'r') as f:
            return json.load(f)
    return []

def scrape_newspaper():
    url = "https://www.timesnewspapers.com/search/?l=100"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    existing_articles = load_existing_articles()
    existing_titles = set(article['title'] for article in existing_articles)
    
    new_articles = []
    
    article_containers = soup.select('div.card-container')
    
    print(f"Number of article containers found: {len(article_containers)}")
    
    if not article_containers:
        print("No article containers found. The website structure might have changed.")
        return new_articles

    for i, article in enumerate(article_containers):
        try:
            print(f"\nProcessing article {i+1}:")
            
            title_elem = article.select_one('h3')
            link_elem = article.select_one('a')
            summary_elem = article.select_one('p.tnt-summary')
            image_elem = article.select_one('img')
            date_elem = article.select_one('time')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                
                # Skip this article if the title already exists
                if title in existing_titles:
                    print(f"Skipping duplicate article: {title}")
                    continue
                
                link = link_elem['href']
                summary = summary_elem.text.strip() if summary_elem else "No summary available"
                
                if not link.startswith('http'):
                    link = f"https://www.timesnewspapers.com{link}"
                
                image_url = get_image_url(image_elem)
                if image_url and not image_url.startswith('http'):
                    image_url = f"https://www.timesnewspapers.com{image_url}"
                
                date = None
                if date_elem and 'datetime' in date_elem.attrs:
                    date_str = date_elem['datetime']
                    try:
                        date = datetime.datetime.fromisoformat(date_str).isoformat()
                    except ValueError:
                        print(f"Could not parse date: {date_str}")
                
                new_articles.append({
                    'title': title, 
                    'link': link, 
                    'summary': summary,
                    'image_url': image_url,
                    'date': date
                })
                print(f"New Article Found: {title}")
                if image_url:
                    print(f"Image URL: {image_url}")
                if date:
                    print(f"Date: {date}")
            else:
                print("Incomplete article data found")
        except Exception as e:
            print(f"Error processing an article: {e}")
    
    print(f"\nTotal new articles found: {len(new_articles)}")
    
    # Combine new articles with existing ones and save
    all_articles = existing_articles + new_articles
    with open('scraped_articles.json', 'w') as f:
        json.dump(all_articles, f)

    print(f"Added {len(new_articles)} new articles. Total articles: {len(all_articles)}")
    return new_articles

if __name__ == "__main__":
    scrape_newspaper()