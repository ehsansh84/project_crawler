from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from publics import Consts


async def send_telegram_message(message, apply_link):
    bot = Bot(token=Consts.BOT_TOKEN)

    # Create the Apply button
    apply_button = {"text": "Apply", "url": apply_link}

    # Add the button to an InlineKeyboardMarkup
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[apply_button]])

    # Send the message with the Apply button
    await bot.send_message(chat_id=Consts.TELEGRAM_USER_ID, text=message, reply_markup=reply_markup, parse_mode='Markdown')
