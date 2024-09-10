import requests
from bs4 import BeautifulSoup
import feedgenerator
import datetime

# Function to scrape the newspaper website
def scrape_newspaper():
    url = "https://www.timesnewspapers.com/search/?l=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    # Adjust the selector based on the website's structure
    for article in soup.select('div.card-container'):
        title = article.select_one('h3').text.strip()
        link = article.select_one('h3 a')['href']
        summary = article.select_one('p.tnt-summary').text.strip()
        articles.append({'title': title, 'link': link, 'summary': summary})
    
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
    
    # Save the RSS feed to a file
    with open('webster_kirwood_times_feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    
    print("RSS feed generated successfully!")