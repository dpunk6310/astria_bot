from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from loguru import logger

# locale imports
from data.config import BOT_TOKEN
from data.config import PLACE

# bot
bot = Bot(token=BOT_TOKEN, validate_token=True)

if PLACE in ["docker"]:
    storage = RedisStorage(host="redisdb")
elif PLACE == "test":
    storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logger.add("logs/debug.log", diagnose=False)
