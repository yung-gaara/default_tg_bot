from typing import Dict

from telebot import types


class BotKeyboard:
    def __init__(
        self,
        keys: Dict,
        row_width: int = 2,
    ):
        self.keyboard: types.InlineKeyboardMarkup = self.create_keyboard(keys, row_width)
        self.repeat: types.InlineKeyboardMarkup = self.create_keyboard({"repeat": "Repeat"}, 1)

    @staticmethod
    def create_keyboard(keys: Dict, row_width: int) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        keys_list = []
        for key, description in keys.items():
            button = types.InlineKeyboardButton(text=description, callback_data=key)
            keys_list.append(button)
        keyboard.add(*keys_list, row_width=row_width)
        return keyboard
