import os


def get_api_key_headers() -> str:
    api_key = get_api_key()

    if not api_key:
        raise ValueError(f"CAST_AI_API_KEY was not set in secrets.env file or file was not found")
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key
    }
    return headers


def get_api_key() -> str:
    return os.getenv('CAST_AI_API_KEY')
