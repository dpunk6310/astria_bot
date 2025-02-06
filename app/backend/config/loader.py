from ..telegram_api import TelegramSyncClient
from .settings import BOT_TOKEN

# api
telegram_api = TelegramSyncClient(BOT_TOKEN)
