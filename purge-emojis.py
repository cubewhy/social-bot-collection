import os
import sys
import dotenv

from discord.userbot.bot import DiscordUserbot


dotenv.load_dotenv()


def main():
    # read the Discord token
    discord_token = os.getenv("DISCORD_TOKEN")

    if discord_token is None:
        print("Discord token is None, please set it manually via environment val \"DISCORD_TOKEN\"")
        sys.exit(1)

    # Initialize the userbot
    bot = DiscordUserbot(discord_token)

    # ask for info
    # ask server id
    server_id = input("What's your server id? ")
    if not server_id.strip():
        print("Empty server id received. Quitting...")
        sys.exit(1)

    # ask prefix
    emoji_prefix = input("Emoji prefix: ")

    print("Loading emojis...")
    emojis = bot.emoji_service.query_emojis(server_id)
    # filter emojis
    for emoji in emojis:
        emoji_name: str = emoji["name"]
        if not emoji_name.startswith(emoji_prefix):
            continue
        
        emoji_id: str = emoji["id"]
        print(f"Purging {emoji_name} ({emoji_id})")
        # delete the emoji
        bot.emoji_service.delete_emoji(server_id, emoji_id)


if __name__ == "__main__":
    main()
