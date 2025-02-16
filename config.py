from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY is missing! Please check .env file")

PACK_SIZE = 10

DEBUG = True
