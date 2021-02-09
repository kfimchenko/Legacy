from io import BytesIO
import json
import os
from pdf2image import convert_from_bytes
from typing import Optional, Sequence, Union, Type
from urllib import request
from loguru import logger
from filetype import guess

from dotenv import load_dotenv
from PIL import Image
from telebot.types import InputMediaPhoto, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, codes

from bot.constants import PASTVU_API_URL, PASTVU_IMAGE_URL, WELCOME_MESSAGE, SEND_LOCATION_MESSAGE
from bot.tele_bot import TeleBot
from parsers.object_info import Location, ObjectInfo, parse_object_info

load_dotenv()

# Send logs to a file
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')

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

        bot.send_chat_action(chat_id, action='Typing')

        location = message.location
        # location = Location(latitude=55.790996, longitude=37.5839)
        object_info = load_object_info(location)

        if object_info is not None:
            logger.debug('Object has been found')

            photo_url = object_info.photo_url
            text = make_object_text(object_info)
            precise_location = object_info.location
            photos = []

            if photo_url is not None:
                photo = load_photo(photo_url)
                photos.append(photo)

            photos += load_retro_photos(location)

            if len(photos) == 1:
                logger.debug('Sending single photo')

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

                    logger.debug('Sending media group')

                    bot.send_media_group(chat_id, media_items)
                else:
                    logger.debug('Sending text without photos')
                    bot.send_message(chat_id, text=text)

            # Send map with precise object location
            if precise_location is not None:
                logger.debug('Sending location')
                bot.send_location(chat_id, **vars(precise_location))
        else:
            logger.debug('Nothing found')
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

    logger.debug(response.url)

    if response.status_code == codes.ok:
        return parse_object_info(response.json())
    else:
        logger.warning(f'Wrong response status code: {response.status_code}, {response.text}')

    return None


def load_retro_photos(location: Location, num_of_photos: int = 3) -> Sequence[bytes]:
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

    logger.debug('Retro photos has been loaded')
    logger.debug(response.json())

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


def parse_retro_photos(data: dict) -> Sequence[bytes]:
    return list(
        map(
            lambda photo: load_photo(f"{PASTVU_IMAGE_URL}{photo.get('file')}"),
            data.get('result').get('photos')
        )
    )


def load_photo(url: str, max_size: Optional[int] = 1200) -> Optional[bytes]:
    file = request.urlopen(url).read()
    file_type = guess(file)

    if file_type is None:
        return None

    if file_type.mime == 'application/pdf':
        logger.debug('PDF file detected. Converting to JPEG')
        file = convert_from_bytes(file, fmt='jpeg')
        logger.debug(f'Converted to jpeg. Type: {type(file)}, {len(file)}')

        if isinstance(file, list) and len(file) > 0:
            file = file.pop(0)
            file = image_to_bytes(file)
        else:
            return None

    file = resize_image(file, max_size)

    return file


def image_to_bytes(image: Image) -> bytes:
    image_buffer = BytesIO()
    image.save(fp=image_buffer, format=image.format)
    img_bytes = image_buffer.getvalue()

    return img_bytes


def resize_image(image: bytes, max_size: int) -> Image:
    image = Image.open(BytesIO(image))
    image_is_too_big = max_size and (image.width > max_size or image.height > max_size)

    if not image_is_too_big:
        return image

    logger.debug(f'Large image detected. Resizing to {max_size}px')

    image.thumbnail((max_size, max_size))

    return image


bot.polling(none_stop=True)
