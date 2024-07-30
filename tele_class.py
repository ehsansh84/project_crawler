import os
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from dotenv import load_dotenv
from publics import Consts
# load_dotenv()
# load_dotenv('.local_env')


async def send_telegram_message(message, apply_link):
    # bot_token = os.getenv('BOT_TOKEN')
    # user_id = os.getenv('USER_ID')
    bot = Bot(token=Consts.BOT_TOKEN)

    # Create the Apply button
    apply_button = {"text": "Apply", "url": apply_link}

    # Add the button to an InlineKeyboardMarkup
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[apply_button]])

    # Send the message with the Apply button
    await bot.send_message(chat_id=Consts.TELEGRAM_USER_ID, text=message, reply_markup=reply_markup, parse_mode='Markdown')
