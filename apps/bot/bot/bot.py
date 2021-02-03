import os
from urllib import request

from dotenv import load_dotenv
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, codes

from bot.constants import WELCOME_MESSAGE, SEND_LOCATION_MESSAGE
from bot.tele_bot import TeleBot

load_dotenv()

api_url = os.getenv('API_URL')
bot_token = os.getenv('BOT_TOKEN')


bot = TeleBot(bot_token, parse_mode='Markdown')

# Add location request button
send_location_button = KeyboardButton(SEND_LOCATION_MESSAGE, request_location=True)
welcome_reply_markup = ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
welcome_reply_markup.add(send_location_button)


@bot.message_handler(commands=['start'])
def welcome(message: Message):
    bot.reply_to(message, WELCOME_MESSAGE, reply_markup=welcome_reply_markup)


@bot.message_handler(func=lambda _: True, content_types=['text', 'location'])
def process_message(message: Message):
    if message.content_type == 'location' and message.location is not None:
        # params = dict(
        #     lat=message.location.latitude,
        #     long=message.location.longitude
        # )
        params = dict(
            lat=51.529903,
            long=46.034597
        )
        response = get(url=api_url + "/v1/find", params=params)
        chat_id = message.chat.id

        if response.status_code == codes.ok:
            data = parse_object_info(response.json())
            photo_url = data.get('photo_url')
            text = f"*{data.get('name')}*, {data.get('date')}{os.linesep}{os.linesep}{data.get('address')}"
            location = data.get('location')

            if photo_url is not None:
                bot.send_chat_action(chat_id, action='upload_photo')
                photo = load_photo(photo_url)
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=text,
                )
            else:
                bot.send_message(chat_id, text=text)

            # Send map with precise object location
            if location is not None:
                bot.send_chat_action(chat_id, action='find_location')
                bot.send_location(chat_id, longitude=location[0], latitude=location[1])
        else:
            bot.send_message(chat_id, text='Ничего не нашли :(')
    else:
        welcome(message)


def parse_object_info(data):
    return {
        'name': data.get('data', {}).get('general', {}).get('name'),
        'date': data.get('data', {}).get('general', {}).get('createDate'),
        'address': data.get('data', {}).get('general', {}).get('address', {}).get('fullAddress'),
        'location': data.get('data', {}).get('general', {}).get('address', {}).get('mapPosition', {}).get('coordinates'),
        'photo_url': data.get('data', {}).get('general', {}).get('photo', {}).get('url'),
    }


def load_photo(url):
    return request.urlopen(url).read()


def main():
    bot.polling(none_stop=True)
