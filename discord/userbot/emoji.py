import requests
import base64

from discord.userbot.utils import build_discord_restapi_headers


class EmojiService:
    def __init__(self, token: str):
        self.token = token

    def upload_emoji(self, server_id: str, emoji_name: str, image: bytes):
        image_base64 = base64.b64encode(image).decode('utf-8')

        r = requests.post(
            f"https://discord.com/api/v9/guilds/{server_id}/emojis",
            json={
                "image": f"data:image/webp;base64,{image_base64}",
                "name": emoji_name
            },
            headers=build_discord_restapi_headers(self.token)
        )
        print(r.json())

    def query_emojis(self, server_id: str):
        r = requests.get(
            f"https://discord.com/api/v9/guilds/{server_id}/emojis",
            headers=build_discord_restapi_headers(self.token)
        )
        return r.json()

    def delete_emoji(self, server_id: str, emoji_id: str):
        requests.delete(
            f"https://discord.com/api/v9/guilds/{server_id}/emojis/{emoji_id}",
            headers=build_discord_restapi_headers(self.token)
        )
