import requests
from bs4 import BeautifulSoup
import feedgenerator
import datetime
import os

# Function to scrape the newspaper website
def scrape_newspaper():
    url = "https://www.timesnewspapers.com/search/?l=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    
    # Select all divs with class 'card-container'
    article_containers = soup.select('div.card-container')

    print(soup.prettify())

    
    print(f"Number of article containers found: {len(article_containers)}")
    
    if not article_containers:
        print("No article containers found. The website structure might have changed.")
        return articles

    for i, article in enumerate(article_containers):
        try:
            print(f"\nProcessing article {i+1}:")
            print(article.prettify())  # Print the HTML of each article for debugging
            
            title_elem = article.select_one('h3')
            link_elem = article.select_one('a')
            summary_elem = article.select_one('p.tnt-summary')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                link = link_elem['href']
                summary = summary_elem.text.strip() if summary_elem else "No summary available"
                
                if not link.startswith('http'):
                    link = f"https://www.timesnewspapers.com{link}"
                
                articles.append({'title': title, 'link': link, 'summary': summary})
                print(f"Article Found: {title}")
            else:
                print("Incomplete article data found")
                if not title_elem:
                    print("Title element not found")
                if not link_elem:
                    print("Link element not found")
        except Exception as e:
            print(f"Error processing an article: {e}")
    
    print(f"\nTotal articles found: {len(articles)}")
    return articles

# Function to generate RSS feed
def generate_rss(articles):
    feed = feedgenerator.Rss201rev2Feed(
        title="Webster Kirwood Times RSS Feed",
        link="https://www.timesnewspapers.com/",
        description="Latest news from our Webster Kirwood Times",
        language="en",
    )
    
    for article in articles:
        feed.add_item(
            title=article['title'],
            link=article['link'],
            description=article['summary'],
            pubdate=datetime.datetime.now()
        )
    
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