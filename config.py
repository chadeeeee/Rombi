import os
from dotenv import load_dotenv

load_dotenv(".env")

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
URI = os.getenv('URI')
