import json
import os
import typing
from pathlib import Path

BASE_PATH = Path(__file__)


def make_in_out_dirs():
    (BASE_PATH / Path("../in")).mkdir(exist_ok=True)


TB_API_TOKEN = os.environ.get("TB_API_TOKEN")
TB_WEBHOOK_HOST = os.environ.get("TB_WEBHOOK_HOST")
TB_WEBHOOK_PORT = int(str(os.environ.get("TB_WEBHOOK_PORT")))
TB_WEBHOOK_LISTEN = os.environ.get("TB_WEBHOOK_LISTEN")
TB_API_URL = os.environ.get("TB_API_URL")
TB_SERVER_HOST = "0.0.0.0"
TB_SERVER_PORT = int(str(os.environ.get("TB_SERVER_PORT")))
TB_WEBHOOK_SSL_CERT = os.environ.get("TB_WEBHOOK_SSL_CERT")
TB_WEBHOOK_SSL_PRIV = os.environ.get("TB_WEBHOOK_SSL_PRIV")
TB_WEBHOOK_URL_BASE = f"https://{TB_WEBHOOK_HOST}:{TB_WEBHOOK_PORT}"
TB_WEBHOOK_URL_PATH = f"/{TB_API_TOKEN}/"

TB_COMMON_TEXT = os.getenv("TB_COMMON_TEXT", "Test bot")
TB_START_PROCESSING_TEXT = os.getenv("TB_START_PROCESSING_TEXT", "Processing...")
TB_WORKER_ERROR_TEXT = os.getenv("TB_WORKER_ERROR_TEXT", "Worker error")
TB_BAD_REQUEST_TEXT = os.getenv("TB_BAD_REQUEST_TEXT", "Bad request.")
TB_SERVER_ERROR_TEXT = os.getenv("TB_SERVER_ERROR_TEXT", "Server error")
TB_BOT_ERROR_TEXT = os.getenv("TB_BOT_ERROR_TEXT", "Bot error")
TB_VIDEO_BUTTON_TEXT = os.getenv("TB_VIDEO_BUTTON_TEXT", "Send video")
TB_AUDIO_BUTTON_TEXT = os.getenv("TB_AUDIO_BUTTON_TEXT", "Send audio")
TB_IMAGE_BUTTON_TEXT = os.getenv("TB_IMAGE_BUTTON_TEXT", "Send image")
TB_TEXT_BUTTON_TEXT = os.getenv("TB_TEXT_BUTTON_TEXT", "Send message")

SERVER_TOKEN = os.getenv("SERVER_TOKEN", "12345")

# Keyboard configs
DEFAULT_KEYS = '{"video": "Video", "audio": "Audio", "text": "Text", "image": "Image"}'
KEYS = json.loads(os.environ.get("KEYS", DEFAULT_KEYS))
KEYBOARD_WIDTH = int(os.getenv("KEYBOARD_WIDTH", 2))

DEFAULT_CONTENT_TYPES = (
    '["video/mp4", "video/x-msvideo", "video/x-m4v", "video/quicktime", "audio/mpeg", '
    '"audio/ogg", "audio/vnd.wav", "audio/x-wav", "audio/opus", "text/plain", "image/jpeg", '
    '"image/png"] '
)
SUPPORT_CONTENT_TYPES = json.loads(os.environ.get("SUPPORT_CONTENT_TYPES", DEFAULT_CONTENT_TYPES))
EXTRA_CONTENT_TYPES: typing.Optional[dict] = None
if "EXTRA_CONTENT_TYPES" in os.environ:
    EXTRA_CONTENT_TYPES = json.loads(os.environ.get("EXTRA_CONTENT_TYPES", ""))
