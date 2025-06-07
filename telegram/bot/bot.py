from telegram.bot.file import FileService
from telegram.bot.sticker import StickerService


class TelegramBot(object):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.sticker_service = StickerService(token)
        self.file_service = FileService(token)