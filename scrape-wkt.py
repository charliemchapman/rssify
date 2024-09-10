import requests
from bs4 import BeautifulSoup
import feedgenerator
import datetime
import os

# Function to scrape the newspaper website
def get_image_url(img_elem):
    if img_elem:
        if 'srcset' in img_elem.attrs:
            # Parse srcset and get the first (usually largest) image URL
            srcset = img_elem['srcset'].split(',')
            if srcset:
                last_src = srcset[-1].strip().split(' ')[0]
                return last_src
        elif 'src' in img_elem.attrs and not img_elem['src'].startswith('data:'):
            return img_elem['src']
    return None

def scrape_newspaper():
    url = "https://www.timesnewspapers.com/search/?l=100"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    
    article_containers = soup.select('div.card-container')
    
    print(f"Number of article containers found: {len(article_containers)}")
    
    if not article_containers:
        print("No article containers found. The website structure might have changed.")
        return articles

    for i, article in enumerate(article_containers):
        try:
            print(f"\nProcessing article {i+1}:")
            
            title_elem = article.select_one('h3')
            link_elem = article.select_one('a')
            summary_elem = article.select_one('p.tnt-summary')
            image_elem = article.select_one('img')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                link = link_elem['href']
                summary = summary_elem.text.strip() if summary_elem else "No summary available"
                
                if not link.startswith('http'):
                    link = f"https://www.timesnewspapers.com{link}"
                
                image_url = get_image_url(image_elem)
                # if image_url and not image_url.startswith('http'):
                #     image_url = f"https://www.timesnewspapers.com{image_url}"
                
                articles.append({
                    'title': title, 
                    'link': link, 
                    'summary': summary,
                    'image_url': image_url
                })
                print(f"Article Found: {title}")
                if image_url:
                    print(f"Image URL: {image_url}")
            else:
                print("Incomplete article data found")
        except Exception as e:
            print(f"Error processing an article: {e}")
    
    print(f"\nTotal articles found: {len(articles)}")
    return articles

def generate_rss(articles):
    feed = feedgenerator.Rss201rev2Feed(
        title="Webster Kirwood Times",
        link="https://www.timesnewspapers.com/",
        description="Latest news from our Webster Kirwood Times",
        language="en",
    )
    
    for article in articles:
        item = {
            'title': article['title'],
            'link': article['link'],
            'description': article['summary'],
            'pubdate': datetime.datetime.now(),
        }
        if article['image_url']:
            item['enclosure'] = feedgenerator.Enclosure(
                url=article['image_url'],
                length='0',
                mime_type='image/jpeg'
            )
        feed.add_item(**item)
    
    return feed.writeString('utf-8')

# Main execution
if __name__ == "__main__":
    articles = scrape_newspaper()
    rss_feed = generate_rss(articles)
    
    # Create the 'feeds' directory if it doesn't exist
    feeds_dir = 'feeds'
    os.makedirs(feeds_dir, exist_ok=True)
    
    # Save the RSS feed to a file in the 'feeds' directory
    file_path = os.path.join(feeds_dir, 'webster_kirwood_times_feed.xml')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    
    print("RSS feed generated successfully!")