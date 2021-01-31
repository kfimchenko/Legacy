import os

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests

from bot.constants import WELCOME_MESSAGE, SEND_LOCATION_MESSAGE

load_dotenv()

api_url = os.getenv('API_URL')
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
    if message.content_type == 'location' and message.location is not None:
        params = dict(
            lat=message.location.latitude,
            long=message.location.longitude
        )
        response = requests.get(url=api_url + "/v1/find", params=params)

        if response.status_code == requests.codes.ok:
            data = response.json()
            bot.reply_to(message, data['data']['general']['name'], reply_markup=removeKeyboardMarkup)
        else:
            bot.reply_to(message, 'Ничего не нашли :(', reply_markup=removeKeyboardMarkup)
    else:
        welcome(message)


def main():
    bot.polling(none_stop=True)
