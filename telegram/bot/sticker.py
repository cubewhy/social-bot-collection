import requests


class StickerService:
    def __init__(self, token):
        self.token = token

    def query_sticker_pack(self, pack_name: str):
        r = requests.get(f"https://api.telegram.org/bot{self.token}/getStickerSet?name={pack_name}")
        response = r.json()
        if not response["ok"]:
            raise Exception(response["error"])
        result = response["result"]
        # stickers: list
        stickers: list = result["stickers"]
        return stickers
