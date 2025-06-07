from discord.userbot.emoji import EmojiService


class DiscordUserbot(object):
    def __init__(self, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.emoji_service = EmojiService(token)