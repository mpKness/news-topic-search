import requests
from bs4 import BeautifulSoup
from scraper import fetch_news, parse_news
import feedparser
from urllib.parse import urlparse
import argparse
import json

def main(topic=None):
    listOfAPIs = [ # TODO: most these apis needs some kinds of setup to connect to
        "https://newsapi.org/v2/top-headlines",
        "https://gnews.io/api/v4/top-headlines",
        "http://api.mediastack.com/v1/news",
        "https://api.currentsapi.services/v1/latest-news",
        "https://content.guardianapis.com/search",
    ]

    listOfRssFeeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "http://rss.cnn.com/rss/edition.rss",
        "https://www.reutersagency.com/feed/?best-topics=world",
        "https://www.theguardian.com/world/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://news.google.com/rss",
    ]

    # Dictionary mapping of websites to where they keep their articles
    site_tags = {
        "bbc.co.uk": {"data-component": "text-block"},
    }

    if topic is None:
        topic = input("Enter the topic you want to search for: ")

    filtered_entries, numberOfArticles = filter_rss_feeds(listOfRssFeeds, topic)
    entries_info = [{"title": entry.title, "link": entry.link} for entry in filtered_entries]


    if filtered_entries:
        first_entry_url = filtered_entries[1].link
        base_url = urlparse(first_entry_url).netloc
        tag = site_tags.get(base_url, {"data-component": "article-body"})  # Default to 'article-body' if the site is not in the dictionary
        full_article = fetch_full_article(first_entry_url, tag)
        print(f"Full article:\n{full_article}")

    return entries_info, numberOfArticles

def filter_rss_feeds(feeds, topic):
    filtered_entries = []
    numberOfEntries = 0
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        numberOfEntries += len(feed.entries)
        for entry in feed.entries:
            if (hasattr(entry, 'title') and topic.lower() in entry.title.lower()) or \
               (hasattr(entry, 'description') and topic.lower() in entry.description.lower()):
                filtered_entries.append(entry)
    return filtered_entries, numberOfEntries

def fetch_full_article(url, tag):
    response = requests.get(url)
    if response.status_code == 200:
        print(f"URL: {url}  TAG:{tag}")
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text based on the provided tag
        elements = soup.find_all('p')
        article_text = '\n'.join([element.get_text() for element in elements])
        return article_text
    else:
        return "Failed to retrieve the full article"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for news articles by topic.")
    parser.add_argument('--topic', type=str, help='The topic to search for')
    args = parser.parse_args()

    entries_info, numberOfArticles = main(args.topic)
    print(json.dumps(entries_info, indent=2))
