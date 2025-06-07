import os
import sys
import requests

from dotenv import load_dotenv

from discord.userbot.bot import DiscordUserbot
from telegram.bot.bot import TelegramBot

load_dotenv()


def main():
    # read token from env
    discord_token = os.getenv("DISCORD_TOKEN")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if len(sys.argv) != 3:
        print("main.py <telegram sticker name> <dc server id>")
        sys.exit(1)
    sticker_set_name = sys.argv[1]
    discord_server_id = sys.argv[2]

    telegram_bot = TelegramBot(telegram_bot_token)
    discord_bot = DiscordUserbot(discord_token)
    print(f"Use sticker set: {sticker_set_name}")

    stickers0 = telegram_bot.sticker_service.query_sticker_pack(sticker_set_name)
    # filter animated
    stickers = [{
        "file_id": v["file_id"]
    } for v in stickers0 if not v["is_animated"] and not v["is_video"]]
    if len(stickers) == 0:
        print("Animated stickers are not supported yet.")
        sys.exit(1)

    # download stickers and upload to Discord
    for i, sticker in enumerate(stickers):
        print(f"Downloading sticker [{i + 1}]")
        raw_file = telegram_bot.file_service.download_telegram_file(sticker["file_id"])
        # upload to discord
        try:
            print(f"Uploading [{i + 1}]")
            emoji_name = f"tg_{sticker_set_name}_{i}"
            discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, raw_file)
            print(f"Successfully uploaded {emoji_name} [{i + 1}]")
        except requests.exceptions.RequestException:
            print(f"Failed to import sticker [{i + 1}]")


if __name__ == '__main__':
    main()
