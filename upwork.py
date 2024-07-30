import feedparser, os
from publics import db, mdb, create_hash
from tele_class import send_telegram_message
import re
import asyncio
from bs4 import BeautifulSoup


col_project = mdb()['project']

upwork_rss_url = os.getenv('upwork_rss_url')


def extract(type, s):
    patterns = {
        'budget': r'Budget</b>: \$(\d+)',
        'hourly_range': r'Hourly Range</b>: \$([\d.]+)-\$([\d.]+)',
        'category': r'Category</b>: (.*?)<',
        'country': r'<br /><b>Country<\/b>: ([^<]+)',
        'skills': r'Skills</b>: (.*?)<',
        'posted_on': r'Posted On</b>: (.*?)<',
    }

    match = re.search(patterns[type], s)
    if match:
        return match.group(1)
    else:
        return -1


def prepare_message(message):
    skills_pattern = r'<b>Skills<\/b>:(.*?)<br \/>'
    skills_second_pattern = r'<b>Skills<\/b>:[^<]*'
    category_pattern = r'<b>Category<\/b>:(.*?)<br \/>'
    posted_on_pattern = r'<b>Posted On<\/b>:(.*?)<br \/>'
    country_pattern = r'<b>Country<\/b>:[^<]*'
    link_pattern = r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)<\/a>'
    hourly_range = r'<b>Hourly Range<\/b>:[^<]*'

    message = re.sub(skills_pattern, '', message)
    message = re.sub(skills_second_pattern, '', message)
    message = re.sub(posted_on_pattern, '', message)
    message = re.sub(category_pattern, '', message)
    message = re.sub(country_pattern, '', message)
    message = re.sub(link_pattern, '', message)
    message = re.sub(hourly_range, '', message)

    return BeautifulSoup(message, 'html.parser').get_text()


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
    i = 0
    for entry in feed.entries:
        item = {
            'title': entry.title[:-9],
            'url': entry.link[:-11],
            'published': entry.published,
            'summary': entry.summary,
            'budget': int(extract('budget', entry.summary)),
            'hourly_range': extract('hourly_range', entry.summary),
            'category': extract('category', entry.summary).replace('&amp;', '&'),
            'country': extract('country', entry.summary).replace('\n', ''),
            'skills': extract('skills', entry.summary),
            'posted_on': extract('posted_on', entry.summary)
        }

        url_hash = create_hash(item['url'])
        item['url_hash'] = url_hash
        if col_project.find_one({'url_hash': url_hash}) is None:
            col_project.insert_one(item)
        budget = f'Budget: {item["budget"]}$' if item["budget"] != -1 else f'Hourly range: {item["hourly_range"]}'

        message = prepare_message(item['summary'])
        # print(message)
        # print('1111111111')
        message = f'''
        {budget}
        🇬🇧
        Category: {item["category"]}
        Country: {item["country"]}
        Skills: {','.join([skill.strip() for skill in item['skills'].split(',')])}
        
        {message}
        '''
        asyncio.run(send_telegram_message(message=message, apply_link=item['url']))

        parsed_data.append(item)
        i += 1
        if i >= 1:
            break

    return parsed_data


parsed_upwork_data = parse_upwork_rss(upwork_rss_url)
