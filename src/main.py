import requests
from bs4 import BeautifulSoup
from scraper import fetch_news, parse_news
import feedparser
from urllib.parse import urlparse
import argparse
import json

# Define a global variable for debug mode
DEBUG_MODE = False

def main(topic=None, debug=False):
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    listOfAPIs = [ # TODO: most these apis need some kinds of setup to connect to
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
        "bbc.co.uk": {"tag-type": "p"},
    }

    if topic is None:
        topic = input("Enter the topic you want to search for: ")

    filtered_entries, numberOfArticles = filter_rss_feeds(listOfRssFeeds, topic)
    if filtered_entries:
        entries_info = []
        for entry in filtered_entries:
            entry_url = entry.link
            base_url = urlparse(entry_url).netloc
            tagType = site_tags.get(base_url, {"tag-type": "p"})  # Default to 'p' if the site is not in the dictionary
            full_article = fetch_full_article_by_tag(entry_url, tagType['tag-type'])

            #if DEBUG_MODE:
            #    with open('debug.log', 'a') as debug_file:
            #        debug_file.write(f"Full article:\n{full_article}\n")
            
            entry_info = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "source": entry.source.title if hasattr(entry, 'source') else None,
                "base_url": base_url,
                "full_article": full_article
            }
            entries_info.append(entry_info)

        if DEBUG_MODE:
            with open('debug.log', 'w') as debug_file:
               debug_file.write(f"Filtered entries: {json.dumps(entries_info, indent=2)}\n")    
    else:
        entries_info = []


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

def fetch_full_article_by_tag(url, tag):
    print(f"Fetching full article from {url} using tag {tag}...")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text based on the provided tag
        elements = soup.find_all(tag)
        article_text = '\n'.join([element.get_text() for element in elements])
        return article_text
    else:
        return "Failed to retrieve the full article"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for news articles by topic.")
    parser.add_argument('--topic', type=str, help='The topic to search for', default=None)
    parser.add_argument('--to_file', type=bool, help='Save the output to a file', default=False)
    parser.add_argument('--debug', type=bool, help='Add extra debug information', default=False)
    args = parser.parse_args()

    entries_info, numberOfArticles = main(args.topic, args.debug)

    if args.to_file:
        with open('news_articles.json', 'w') as file:
            json.dump(entries_info, file, indent=2)
    else:
        print(json.dumps(entries_info, indent=2))
