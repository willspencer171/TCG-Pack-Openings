from dotenv import load_dotenv
import os
from pokemontcgsdk import RestClient

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY is missing! Please check .env file")

RestClient.configure(API_KEY)

PACK_SIZE = 10

DEBUG = True
