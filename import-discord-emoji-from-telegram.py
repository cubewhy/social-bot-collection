import os
import sys
import traceback
from enum import Enum, auto

import requests

from dotenv import load_dotenv

from discord.userbot.bot import DiscordUserbot
from telegram.bot.bot import TelegramBot
from utils import video_bytes_to_gif_bytes, tgs_bytes_to_gif_bytes, compress_gif, video_bytes_to_webp_bytes

load_dotenv()


class StickerType(Enum):
    STATIC = auto()
    VIDEO = auto()
    R_LOTTIE = auto()  # not supported yet


def get_sticker_type(sticker: dict):
    # if not v["is_animated"] and not v["is_video"]
    if sticker["is_animated"]:
        return StickerType.R_LOTTIE
    elif sticker["is_video"]:
        return StickerType.VIDEO
    return StickerType.STATIC


def trim_sticker_set_name(name: str) -> str:
    return name[:18]


def main():
    # read token from env
    discord_token = os.getenv("DISCORD_TOKEN")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if len(sys.argv) < 3:
        print("import-discord-emoji-from-telegram.py <telegram sticker name> <dc server id>")
        sys.exit(1)
    sticker_set_name = sys.argv[1]
    discord_server_id = sys.argv[2]
    skip_count = int(sys.argv[3]) if len(sys.argv) >= 4 else 0

    telegram_bot = TelegramBot(telegram_bot_token)
    discord_bot = DiscordUserbot(discord_token)
    print(f"Use sticker set: {sticker_set_name}")

    stickers0 = telegram_bot.sticker_service.query_sticker_pack(sticker_set_name)
    # filter animated
    stickers = [{
        "file_id": v["file_id"],
        "type": get_sticker_type(v)
    } for v in stickers0]
    if len(stickers) == 0:
        print("Animated stickers are not supported yet.")
        sys.exit(1)

    # download stickers and upload to Discord
    for i, sticker in enumerate(stickers):
        if skip_count != 0:
            skip_count -= 1
            continue
        print(f"Downloading sticker [{i + 1}]")
        sticker_type: StickerType = sticker["type"]
        raw_file = telegram_bot.file_service.download_telegram_file(sticker["file_id"])
        # upload to discord
        try:
            print(f"Uploading [{i + 1}]")
            emoji_name = f"tg_{trim_sticker_set_name(sticker_set_name)}_{i}"
            if sticker_type == StickerType.STATIC:
                # static image, upload directly
                discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, raw_file, "image/webp")
            elif sticker_type == StickerType.VIDEO:
                # .mp4 or something
                # convent to webp
                webp_bytes = video_bytes_to_webp_bytes(raw_file, 30, 256)
                discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, webp_bytes, "image/webp")
            else:
                # rLottie files
                gif_bytes = compress_gif(tgs_bytes_to_gif_bytes(raw_file), size=(64, 64))
                discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, gif_bytes, "image/webp")
            print(f"Successfully uploaded {emoji_name} [{i + 1}]")
        except requests.exceptions.RequestException as e:
            print(f"Failed to import sticker [{i + 1}]")
            traceback.print_exc()


if __name__ == '__main__':
    main()
