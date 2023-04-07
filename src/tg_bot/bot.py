import logging
import ssl

import telebot
from aiohttp import web

from tg_bot.ui.bot_ui import BotUI


class BotApp:
    def __init__(
        self,
        config,
    ):
        self.bot: telebot.TeleBot = self.setup_bot(config)
        self.context: ssl.SSLContext = self.setup_ssl(config)
        self.host: str = config.TB_SERVER_HOST
        self.port: int = config.TB_SERVER_PORT
        self.app: web.Application = self.setup_app()
        BotUI(self.bot, config)
        logging.info("Bot has initialized")

    @staticmethod
    def setup_bot(config) -> telebot.TeleBot:
        bot = telebot.TeleBot(config.TB_API_TOKEN)
        bot.chat_id_server = {}
        config.make_in_out_dirs()
        bot.remove_webhook()
        bot.set_webhook(
            url=f"{config.TB_WEBHOOK_URL_BASE}{config.TB_WEBHOOK_URL_PATH}",
            certificate=open(config.TB_WEBHOOK_SSL_CERT, "r"),
        )
        return bot

    def setup_app(self) -> web.Application:
        app = web.Application()
        app.router.add_post("/{token}/", self._handle)
        return app

    def run(self):
        web.run_app(
            self.app,
            host=self.host,
            port=self.port,
            ssl_context=self.context,
        )

    async def _handle(self, request) -> web.Response:
        if request.match_info.get("token") == self.bot.token:
            request_body_dict = await request.json()
            update = telebot.types.Update.de_json(request_body_dict)
            self.bot.process_new_updates([update])
            return web.Response()
        else:
            return web.Response(status=403)

    @staticmethod
    def setup_ssl(config) -> ssl.SSLContext:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config.TB_WEBHOOK_SSL_CERT, config.TB_WEBHOOK_SSL_PRIV)
        return context
