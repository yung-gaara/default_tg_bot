import json
import logging
import mimetypes
import typing as t
from pathlib import Path

from requests import Response
from telebot import TeleBot
from telebot import types
from telebot.types import Audio
from telebot.types import Document
from telebot.types import File
from telebot.types import Message
from telebot.types import PhotoSize
from telebot.types import Video
from telebot.types import VideoNote
from telebot.types import Voice

from tg_bot import config
from tg_bot.components import Warnings

if config.EXTRA_CONTENT_TYPES:
    for key, value in config.EXTRA_CONTENT_TYPES.items():
        mimetypes.add_type(key, value)


def get_message_file(message: Message) -> t.Union[Document, Audio, Voice, Video, PhotoSize, VideoNote, str]:
    if message.document:
        message_file = message.document
    elif message.audio:
        message_file = message.audio
    elif message.voice:
        message_file = message.voice
    elif message.video:
        message_file = message.video
    elif message.photo:
        message_file = message.photo[-1]
    elif message.video_note:
        message_file = message.video_note
    elif message.text:
        message_file = message.text
    else:
        raise RuntimeError("Message doesn't contain anything to process")
    return message_file


def prepare_request(bot: TeleBot, getting_file: File, path: Path) -> Path:
    downloaded_file = bot.download_file(getting_file.file_path)
    input_save_path = Path(getting_file.file_path)

    logging.info(f"File: {input_save_path}")

    file_name = input_save_path.name
    file_path = path / Path(f"../../in/{file_name}")
    with open(file_path, "wb") as new_file:
        new_file.write(downloaded_file)
    return file_path


def validate_message(file_path: t.Optional[Path], content_type: str) -> Warnings:
    if not validate_file_content_type(file_path, content_type):
        return Warnings.wrong_content_type
    return Warnings.ok


def validate_file_content_type(file_path: t.Optional[Path], content_type: str) -> bool:
    if file_path is None:
        file_type: t.Optional[str] = "text"
    else:
        file_type, _ = mimetypes.guess_type(file_path)
    if file_type:
        file_content_type = file_type.split("/")[0]
    else:
        return False
    if file_content_type != content_type:
        return False
    return True


def prepare_data(file_path: Path, content_type: str):
    basename = file_path.name
    mime_type, _ = mimetypes.guess_type(file_path)
    files = {"file": (basename, open(file_path, "rb"), mime_type), "content_type": content_type}
    return files


def postprocessing_result(resp: Response, chat_id: int, reply_markup: types.InlineKeyboardMarkup) -> dict:
    response_message: t.Dict[str, t.Union[str, int, types.InlineKeyboardMarkup]] = dict(
        chat_id=chat_id, reply_markup=reply_markup
    )
    if resp.status_code == 200:
        result = json.loads(resp.text)
        if result["error"]["error_code"]:
            response_message.update(text=f"{config.TB_WORKER_ERROR_TEXT}\n{result['error']['message']}")
            return response_message
        else:
            text = result["result"]
            response_message.update(text=text)
        return response_message
    elif resp.status_code == 400:
        response_message.update(text=config.TB_BAD_REQUEST_TEXT)
        return response_message
    response_message.update(text=config.TB_SERVER_ERROR_TEXT)
    return response_message
