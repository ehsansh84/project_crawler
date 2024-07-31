import feedparser
import os
import re
import asyncio
from bs4 import BeautifulSoup
from publics import mdb, create_hash, Consts
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
import logging
from datetime import datetime

rss_feeds = [
    # Data scraping all
    'https://www.upwork.com/ab/feed/jobs/rss?amount=100-499%2C500-999%2C1000-4999%2C5000-&paging=NaN-undefined&proposals=0-4&q=data%20scraping&sort=recency&t=1&api_params=1&securityToken=54c1632cf771ba88d2938701495407702b8787ba16489fc2dd6224b49c115596c84ca6096ce121cbca2d4ed28a78321c8f36cdf26f0a56cb8e12b7c1e5d6b866&userUid=1298660936886677504&orgUid=1298660936886677506',
    # Data extraction category
    'https://www.upwork.com/ab/feed/jobs/rss?amount=100-499%2C500-999%2C1000-4999%2C5000-&paging=NaN-undefined&proposals=0-4&sort=recency&subcategory2_uid=531770282593251331&t=1&api_params=1&securityToken=54c1632cf771ba88d2938701495407702b8787ba16489fc2dd6224b49c115596c84ca6096ce121cbca2d4ed28a78321c8f36cdf26f0a56cb8e12b7c1e5d6b866&userUid=1298660936886677504&orgUid=1298660936886677506',
]
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

col_project = mdb()['project']
upwork_rss_url = os.getenv('upwork_rss_url')
not_interested_skills = ['TradingView', 'Machine Learning', 'Google Cloud Platform', 'Firebase', 'MetaTrader',
                         'Embedded Application', 'MetaTrader', 'MQL 5', 'MQL 4', 'Forex Trading', 'Blockchain']
interested_skill = ['Data Processing', 'Python', 'Data Scraping', 'WordPress', 'Automation', 'Microsoft Excel', 'Linux',
                    'Automation', 'API', 'Data Extraction', 'Data Entry', 'Web Crawling', 'Scripting', 'Pandas',
                    'Python Script', 'Bot Development', 'Python Script', 'Data Cleaning', 'Data Collection',
                    'Web Scraping', 'Web Crawling', 'API Development']


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
    patterns_to_remove = [
        r'<b>Skills<\/b>:(.*?)<br \/>',
        r'<b>Skills<\/b>:[^<]*',
        r'<b>Category<\/b>:(.*?)<br \/>',
        r'<b>Posted On<\/b>:(.*?)<br \/>',
        r'<b>Country<\/b>:[^<]*',
        r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)<\/a>',
        r'<b>Hourly Range<\/b>:[^<]*'
    ]
    for pattern in patterns_to_remove:
        message = re.sub(pattern, '', message)
    return BeautifulSoup(message, 'html.parser').get_text()


async def send_telegram_message(bot, message, apply_link):
    apply_button = InlineKeyboardButton(text="Apply", url=apply_link)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[apply_button]])
    await bot.send_message(chat_id=Consts.TELEGRAM_USER_ID, text=message, reply_markup=reply_markup, parse_mode='HTML')


def get_budget(item):
    budget = f'Budget: {item["budget"]}$' if item["budget"] != -1 else f'Hourly range: {item["hourly_range"]}'
    if 100 <= item["budget"] < 200:
        budget = '💚' + budget
    elif 200 <= item["budget"] < 300:
        budget = '💛' + budget
    elif item["budget"] > 300:
        budget = '❤️' + budget

    return budget


def get_skills(item):
    result = ''
    for skill in item['skills'].split(','):
        skill = skill.strip()
        if skill in interested_skill:
            skill = f'✅{skill}'
        elif skill in not_interested_skills:
            skill = f'❌{skill}'
        result += skill + ','
    return result


async def parse_upwork_rss(url):
    logging.info("Starting to parse Upwork RSS feed.")
    parsed_data = []
    feed = feedparser.parse(url)
    bot = Bot(token=Consts.BOT_TOKEN)

    try:
        for i, entry in enumerate(feed.entries):
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

                message = prepare_message(item['summary'])
                message = f'''
    {get_budget(item)}
    Category: {item["category"]}
    Country: {item["country"]}
    Skills: {get_skills(item)}

    {message}
    '''[:1000]
                await send_telegram_message(bot, message, item['url'])
                parsed_data.append(item)

    finally:
        await bot.session.close()
        logging.info("Finished parsing Upwork RSS feed.")

    return parsed_data


if __name__ == "__main__":
    logging.info("Script started at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for i in range(5):
        asyncio.run(parse_upwork_rss(upwork_rss_url))
        sleep(10)
    logging.info("Script finished at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))