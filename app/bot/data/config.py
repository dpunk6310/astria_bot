import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django_secret_key_75uYGHJGJKYFKUIy")

BOT_TOKEN = env.str("BOT_TOKEN", default="norm")
PLACE = env.str("PLACE", default="test")
DJANGO_URL = env.str("DJANGO_URL")
