import feedparser
import os
import re
import asyncio
from bs4 import BeautifulSoup
from publics import mdb, create_hash
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

col_project = mdb()['project']
upwork_rss_url = os.getenv('upwork_rss_url')
bot_token = os.getenv('BOT_TOKEN')
user_id = os.getenv('USER_ID')
not_interested_skills = ['TradingView']
interested_skill = ['Data Processing', 'Python', 'Data Scraping', 'WordPress', 'Automation', 'Microsoft Excel', 'Linux',
                    'Automation', 'API', 'Data Extraction', 'Data Entry']


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
    await bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode='HTML')


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
    parsed_data = []
    feed = feedparser.parse(url)
    bot = Bot(token=bot_token)

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

    return parsed_data


if __name__ == "__main__":
    asyncio.run(parse_upwork_rss(upwork_rss_url))
