import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django_secret_key_75uYGHJGJKYFKUIy")

BOT_TOKEN = env.str("BOT_TOKEN", default="norm")
PLACE = env.str("PLACE", default="test")
DJANGO_URL = env.str("DJANGO_URL")
REDIS_PASSWORD = env.str("REDIS_PASSWORD", "")
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", "6379")
REDIS_DB = env.str("REDIS_DB", "0")

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
