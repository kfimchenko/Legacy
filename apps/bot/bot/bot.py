import json
import os
from urllib import request

from dotenv import load_dotenv
from telebot.types import InputMediaPhoto, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, codes

from bot.constants import PASTVU_API_URL, PASTVU_IMAGE_URL, WELCOME_MESSAGE, SEND_LOCATION_MESSAGE
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
        chat_id = message.chat.id
        location = message.location
        object_info = load_object_info(location)
        # params = dict(
        #     lat=51.529903,
        #     long=46.034597
        # )

        if object_info is not None:
            bot.send_chat_action(chat_id, action='upload_photo')
            photo_url = object_info.get('photo_url')
            text = f"*{object_info.get('name')}*, {object_info.get('date')}{os.linesep}{os.linesep}{object_info.get('address')}"
            precise_location = object_info.get('location')
            photos = []

            if photo_url is not None:
                photo = load_photo(photo_url)
                photos.append(photo)

            photos += load_retro_photos(location)

            if len(photos) == 1:
                bot.send_photo(
                    chat_id,
                    photos[0],
                    caption=text,
                )
            else:
                # Send multiple files
                if len(photos) > 1:
                    media_items = [InputMediaPhoto(photos.pop(0), caption=text, parse_mode='Markdown')]
                    media_items += map(lambda file: InputMediaPhoto(file), photos)

                    bot.send_media_group(chat_id, media_items)
                else:
                    bot.send_message(chat_id, text=text)

            # Send map with precise object location
            if precise_location is not None:
                bot.send_chat_action(chat_id, action='find_location')
                bot.send_location(chat_id, longitude=precise_location[0], latitude=precise_location[1])
        else:
            bot.send_message(chat_id, text='Ничего не нашли :(')
    else:
        welcome(message)


def load_object_info(location):
    params = dict(
        lat=location.latitude,
        long=location.longitude
    )
    response = get(url=api_url + "/v1/find", params=params)

    if response.status_code == codes.ok:
        return parse_object_info(response.json())

    return None


def load_retro_photos(location, num_of_photos=3):
    params = dict(
        method='photo.giveNearestPhotos',
        params=json.dumps(
            dict(
                geo=[location.latitude, location.longitude],
                limit=num_of_photos
            )
        )
    )
    response = get(PASTVU_API_URL, params=params)

    if response.status_code == codes.ok:
        return parse_retro_photos(response.json())

    return []


def parse_object_info(data):
    return {
        'name': data.get('data', {}).get('general', {}).get('name'),
        'date': data.get('data', {}).get('general', {}).get('createDate'),
        'address': data.get('data', {}).get('general', {}).get('address', {}).get('fullAddress'),
        'location': data.get('data', {}).get('general', {}).get('address', {}).get('mapPosition', {}).get(
            'coordinates'),
        'photo_url': data.get('data', {}).get('general', {}).get('photo', {}).get('url'),
    }


def parse_retro_photos(data):
    return map(lambda photo: load_photo(f"{PASTVU_IMAGE_URL}{photo.get('file')}"), data.get('result').get('photos'))


def load_photo(url):
    return request.urlopen(url).read()


def main():
    bot.polling(none_stop=True)
