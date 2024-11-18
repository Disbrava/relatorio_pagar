from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
import os
import logging

env_file = os.path.join(Path(__file__).resolve().parent.parent.parent, '.env.test') if os.getenv(
    'ENVIRONMENT') == 'TEST' else os.path.join(Path(__file__).resolve().parent.parent.parent, '.env')

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    raise FileNotFoundError(f"ENVIRONMENT FILE NOT FOUND!")


class Enviroments(str, Enum):
    PRODUCTION = 'PRODUCTION'
    DEVELOPMENT = 'DEVELOPMENT'
    TEST = 'TEST'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file)

    APP_NAME: str = """Serviço Envio de Emails"""
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: Enviroments = Field(default=Enviroments.TEST)
    DATABASE_URL: str = Field()
    ORACLE_USERNAME: str = Field()
    ORACLE_PASSWORD: str = Field()
    ORACLE_HOST: str = Field()
    ORACLE_PORT: int = Field()
    ORACLE_SERVICE_NAME: str = Field()

    SMTP_HOST: str = Field()
    SMTP_PORT: int = Field()
    SMTP_USERNAME: str = Field()
    SMTP_PASSWORD: str = Field()

    SMTP_RECEIVERS: str = Field()

    #Logs to Telegram
    BOT_TOKEN: str = Field()
    CHAT_ID: str = Field()
    TELEGRAM_API_URL: str = Field()
