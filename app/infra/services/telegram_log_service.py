import logging
import os

import requests


class TelegramLogService(logging.Handler):
    def __init__(self, api_url: str, bot_token: str, chat_id: str):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = api_url
        self.env_name = os.getenv('ENVIRONMENT')

    def emit(self, record):
        log_entry = self.format(record)

        payload = {
            'chat_id': self.chat_id,
            "text": f"[{self.env_name}] {log_entry}",
            "parse_mode": "HTML"
        }
        try:
            requests.post(self.api_url, data=payload)
        except Exception as e:
            print(f"Failed to send log to Telegram: {e}")


