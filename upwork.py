import feedparser, os
from publics import db
from tele_class import send_telegram_message
import re
import asyncio
from bs4 import BeautifulSoup

upwork_rss_url = os.getenv('upwork_rss_url')


patterns = {
    'budget': r'Budget</b>: \$(\d+)',
    'hourly_range': r'Hourly Range</b>: \$([\d.]+)-\$([\d.]+)',
    'category': r'Category</b>: (.*?)<',
    'country': r'Country</b>: (.*?)<',
    'skills': r'Skills</b>: (.*?)<',
    'posted_on': r'Posted On</b>: (.*?)<',
}


def extract(type, s):
    match = re.search(patterns[type], s)
    if match:
        return match.group(1)
    else:
        return -1


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
        item['budget'] = extract('budget', entry.summary)
        item['hourly_range'] = extract('hourly_range', entry.summary)
        item['category'] = extract('category', entry.summary)
        item['country'] = extract('country', entry.summary)
        item['budget'] = extract('budget', entry.summary)
        item['skills'] = extract('skills', entry.summary)
        item['posted_on'] = extract('posted_on', entry.summary)

        print(entry)
        # print(item)
        # db().insert(item)
        content = BeautifulSoup(item['summary'], 'html.parser').get_text()

        asyncio.run(send_telegram_message(message='========================'))
        asyncio.run(send_telegram_message(message=content))
        asyncio.run(send_telegram_message(message='========================'))

        parsed_data.append(item)
        break

    return parsed_data


parsed_upwork_data = parse_upwork_rss(upwork_rss_url)
