import requests


class FileService(object):
    def __init__(self, token):
        self.token = token

    def download_telegram_file(self, file_id: str) -> bytes:
        url = f"https://api.telegram.org/bot{self.token}/getFile?file_id={file_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        result = resp.json()

        if not result.get("ok", False):
            raise RuntimeError(result.get("description", "Unknown error from Telegram API"))

        file_path = result["result"]["file_path"]

        file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"

        file_resp = requests.get(file_url)
        file_resp.raise_for_status()

        return file_resp.content
