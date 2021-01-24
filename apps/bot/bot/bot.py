import os

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from bot.constants import WELCOME_MESSAGE, SEND_LOCATION_MESSAGE

load_dotenv()

bot = TeleBot(os.getenv('BOT_TOKEN'), parse_mode='MARKDOWN')

# Add location request button
sendLocationButton = KeyboardButton(SEND_LOCATION_MESSAGE, request_location=True)
replyMarkup = ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
replyMarkup.add(sendLocationButton)

# Remove button
removeKeyboardMarkup = ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def welcome(message: Message):
    bot.reply_to(message, WELCOME_MESSAGE, reply_markup=replyMarkup)


@bot.message_handler(func=lambda _: True, content_types=['text', 'location'])
def process_message(message: Message):
    print(message.content_type)

    if message.content_type == 'location':
        bot.reply_to(message, f'Ваши координаты: {message.location}', reply_markup=removeKeyboardMarkup)
    else:
        welcome(message)


def main():
    bot.polling(none_stop=True)
