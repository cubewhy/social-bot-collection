def build_discord_restapi_headers(token: str, content_type="application/json"):
    return {
        "Authorization": token,
        "Content-Type": content_type,
    }
