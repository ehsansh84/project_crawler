from dotenv import load_dotenv
load_dotenv()

from telegram import Bot
import os


async def send_telegram_message(message):
    bot_token = os.getenv('BOT_TOKEN')
    user_id = os.getenv('USER_ID')
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
