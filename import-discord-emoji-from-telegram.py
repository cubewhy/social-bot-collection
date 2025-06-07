import os
import sys
import time
import traceback

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from tqdm import tqdm
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
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            transient=True,
    ) as progress:
        task = progress.add_task("Processing stickers...", total=len(stickers))

        for i, sticker in enumerate(stickers):
            if skip_count != 0:
                skip_count -= 1
                continue

            progress.update(task, advance=1, description=f"Uploading sticker {i + 1}/{len(stickers)}")
            sticker_type: StickerType = sticker["type"]
            raw_file = telegram_bot.file_service.download_telegram_file(sticker["file_id"])

            for retry in range(5):
                try:
                    emoji_name = f"tg_{trim_sticker_set_name(sticker_set_name)}_{i}"
                    if sticker_type == StickerType.STATIC:
                        r = discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, raw_file,
                                                                   "image/webp")
                    elif sticker_type == StickerType.VIDEO:
                        webp_bytes = video_bytes_to_webp_bytes(raw_file, 30, 256)
                        r = discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, webp_bytes,
                                                                   "image/webp")
                    else:
                        gif_bytes = compress_gif(tgs_bytes_to_gif_bytes(raw_file), size=(64, 64))
                        r = discord_bot.emoji_service.upload_emoji(discord_server_id, emoji_name, gif_bytes,
                                                                   "image/webp")

                    if "message" in r:
                        msg = r["message"]
                        progress.console.print(f"[red]Upload failed:[/] {msg}")
                        if "rate limited" in msg:
                            timeout = int(r["retry_after"]) + 1
                            progress.console.print(f"[yellow]Rate limited. Waiting {timeout}s...[/]")
                            for remaining in range(timeout, 0, -1):
                                time.sleep(1)
                                progress.console.print(f"Retrying in {remaining}s...", end="\r")
                        continue
                    else:
                        break
                except requests.exceptions.RequestException:
                    progress.console.print(f"[red]Network error while uploading sticker {i + 1}[/]")
                    traceback.print_exc()


if __name__ == '__main__':
    main()
