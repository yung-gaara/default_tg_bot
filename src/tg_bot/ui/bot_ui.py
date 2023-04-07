import logging
from io import StringIO
from pathlib import Path
from typing import Dict

import telebot.types
from requests import Response
from requests import Session
from telebot import TeleBot

from tg_bot.components import Warnings
from tg_bot.ui.bot_keyboard import BotKeyboard
from tg_bot.ui.utils import get_message_file
from tg_bot.ui.utils import postprocessing_result
from tg_bot.ui.utils import prepare_data
from tg_bot.ui.utils import prepare_request
from tg_bot.ui.utils import validate_message


class BotUI:
    def __init__(
        self,
        bot: TeleBot,
        config,
    ):
        self.bot: telebot.TeleBot = bot
        self.path: Path = Path(__file__).parent
        self.config = config
        self.bot_keyboard = BotKeyboard(self.config.KEYS, self.config.KEYBOARD_WIDTH)
        bot.message_handler(
            commands=[
                "start",
                "help",
            ]
        )(self.send_description)
        bot.message_handler(
            content_types=[
                "audio",
                "document",
                "photo",
                "video",
                "video_note",
                "voice",
                "text",
            ]
        )(self.handle_file_message)
        bot.message_handler(
            content_types=[
                "text",
                "sticker",
            ]
        )(self.send_description)
        bot.callback_query_handler(func=lambda call: True)(self.buttons_handler)
        self.pressing_button_users: Dict[int, str] = {}
        logging.info("BotUI has initialized")

    def get_user_auth(self, uid: int) -> bool:
        if uid in self.pressing_button_users.keys():
            return True
        else:
            return False

    def send_description(self, message: telebot.types.Message):
        chat_id = message.chat.id
        if not self.pressing_button_users.get(chat_id):
            self.bot.send_message(chat_id, self.config.TB_COMMON_TEXT, reply_markup=self.bot_keyboard.keyboard)

    def request_to_api(self, file_path: Path, content_type: str, message_file) -> Response:
        with StringIO() as f:
            if file_path is None:
                f.write(message_file)
                f.seek(0)
                files = {"file": ("text.txt", f, "text/plain"), "content_type": content_type}
            else:
                files = prepare_data(file_path, content_type)
            with Session() as session:
                result = session.post(url=self.config.TB_API_URL, files=files)
        return result

    def handle_file_message(self, message: telebot.types.Message):
        chat_id = message.chat.id
        if not self.get_user_auth(chat_id):
            self.bot.send_message(chat_id, self.config.TB_COMMON_TEXT, reply_markup=self.bot_keyboard.keyboard)
            return
        content_type = self.pressing_button_users.pop(chat_id)
        logging.info(f"Get file from {chat_id}")
        try:
            message_file = get_message_file(message)
            file_path = None
            if not isinstance(message_file, str):
                file_info = self.bot.get_file(message_file.file_id)
                file_path = prepare_request(self.bot, file_info, self.path)
            validation_result = validate_message(file_path, content_type)
            if validation_result is not Warnings.ok:
                self.bot.send_message(
                    chat_id,
                    validation_result.value,
                    reply_markup=self.bot_keyboard.repeat,
                )
                return
            self.bot.send_message(chat_id, self.config.TB_START_PROCESSING_TEXT)
            resp = self.request_to_api(file_path=file_path, content_type=content_type, message_file=message_file)
            result = postprocessing_result(resp, chat_id, self.bot_keyboard.repeat)
            self.bot.send_message(**result)
        except Exception as e:
            logging.exception(e)
            self.bot.send_message(chat_id, self.config.TB_BOT_ERROR_TEXT, reply_markup=self.bot_keyboard.repeat)

    def buttons_handler(self, call: telebot.types.CallbackQuery):
        if call.data == "video":
            self.bot.send_message(call.message.chat.id, self.config.TB_VIDEO_BUTTON_TEXT)
            self.pressing_button_users.update({call.message.chat.id: call.data})
        elif call.data == "audio":
            self.bot.send_message(call.message.chat.id, self.config.TB_AUDIO_BUTTON_TEXT)
            self.pressing_button_users.update({call.message.chat.id: call.data})
        elif call.data == "text":
            self.bot.send_message(call.message.chat.id, self.config.TB_TEXT_BUTTON_TEXT)
            self.pressing_button_users.update({call.message.chat.id: call.data})
        elif call.data == "image":
            self.bot.send_message(call.message.chat.id, self.config.TB_IMAGE_BUTTON_TEXT)
            self.pressing_button_users.update({call.message.chat.id: call.data})
        elif call.data == "repeat":
            self.bot.send_message(
                call.message.chat.id,
                self.config.TB_COMMON_TEXT,
                reply_markup=self.bot_keyboard.keyboard,
            )
        else:
            self.bot.send_message(
                call.message.chat.id,
                Warnings.wrong_content_type.value,
                reply_markup=self.bot_keyboard.repeat,
            )
        self.bot.answer_callback_query(call.id)
