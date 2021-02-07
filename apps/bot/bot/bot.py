import json
import os
from typing import Optional, Sequence
from urllib import request

from dotenv import load_dotenv
from telebot.types import InputMediaPhoto, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, codes

from bot.constants import PASTVU_API_URL, PASTVU_IMAGE_URL, WELCOME_MESSAGE, SEND_LOCATION_MESSAGE
from bot.tele_bot import TeleBot
from parsers.object_info import Location, ObjectInfo, parse_object_info

load_dotenv()

api_url = os.getenv('API_URL')
bot_token = os.getenv('BOT_TOKEN')

bot = TeleBot(bot_token, parse_mode='Markdown')

# Add location request button
send_location_button = KeyboardButton(SEND_LOCATION_MESSAGE, request_location=True)
welcome_reply_markup = ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
welcome_reply_markup.add(send_location_button)


@bot.message_handler(commands=['start', 'test'])
def welcome(message: Message):
    bot.reply_to(message, WELCOME_MESSAGE, reply_markup=welcome_reply_markup)


@bot.message_handler(func=lambda _: True, content_types=['text', 'location'])
def all_messages_handler(message: Message):
    if message.content_type == 'location' and message.location is not None:
        chat_id = message.chat.id
        location = message.location
        # location = Location(latitude=51.529903, longitude=46.034597)
        object_info = load_object_info(location)

        if object_info is not None:
            bot.send_chat_action(chat_id, action='upload_photo')
            photo_url = object_info.photo_url
            text = make_object_text(object_info)
            precise_location = object_info.location
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
                bot.send_location(chat_id, **vars(precise_location))
        else:
            bot.send_message(chat_id, text='Ничего не нашли :(')
    else:
        welcome(message)


def load_object_info(location: Location) -> Optional[ObjectInfo]:
    params = dict(
        lat=location.latitude,
        long=location.longitude,
        count=3
    )
    response = get(url=api_url + "/v1/find", params=params)

    if response.status_code == codes.ok:
        return parse_object_info(response.json())

    return None


def load_retro_photos(location, num_of_photos=3) -> Sequence[bytes]:
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


def make_object_text(object_info: ObjectInfo) -> str:
    text = f'*{object_info.name}*'

    if object_info.date:
        text += f', {object_info.date}'

    if object_info.distance:
        text += f', {object_info.distance}м до вас'

    if object_info.address:
        text += f'{os.linesep}{os.linesep}{object_info.address}'

    return text


def parse_retro_photos(data) -> Sequence[bytes]:
    return list(map(lambda photo: load_photo(f"{PASTVU_IMAGE_URL}{photo.get('file')}"), data.get('result').get('photos')))


def load_photo(url) -> bytes:
    return request.urlopen(url).read()


def main():
    bot.polling(none_stop=True)
