import feedparser
from dotenv

def parse_upwork_rss(url):
    """
    Parse Upwork RSS feed.

    Parameters:
        url (str): URL of the Upwork RSS feed.

    Returns:
        list: List of dictionaries containing parsed data.
    """
    parsed_data = []
    feed = feedparser.parse(url)

    for entry in feed.entries:
        item = {}
        item['title'] = entry.title
        item['link'] = entry.link
        item['published'] = entry.published
        item['summary'] = entry.summary
        parsed_data.append(item)

    return parsed_data

# Example usage:
upwork_rss_url = 'https://www.upwork.com/ab/feed/topics/rss?securityToken=YourSecurityTokenHere'
parsed_upwork_data = parse_upwork_rss(upwork_rss_url)

# Printing the parsed data
for item in parsed_upwork_data:
    print("Title:", item['title'])
    print("Link:", item['link'])
    print("Published:", item['published'])
    print("Summary:", item['summary'])
    print("-" * 50)
