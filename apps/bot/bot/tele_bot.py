from telebot import TeleBot as OriginalTeleBot
from telebot.types import ReplyKeyboardRemove

# Remove button
removeKeyboardMarkup = ReplyKeyboardRemove()


class TeleBot(OriginalTeleBot):
    def send_message(self, *args, reply_markup=None, **kwargs):
        markup = reply_markup if (reply_markup is not None) else removeKeyboardMarkup
        super().send_message(*args, **kwargs, reply_markup=markup,)

    def send_photo(self, *args, reply_markup=None, **kwargs):
        markup = reply_markup if (reply_markup is not None) else removeKeyboardMarkup
        super().send_photo(*args, **kwargs, reply_markup=markup,)
