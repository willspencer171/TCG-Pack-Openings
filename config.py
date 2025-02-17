from dotenv import load_dotenv
import os
from pokemontcgsdk import RestClient

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY is missing! Please check .env file")

RestClient.configure(API_KEY)

DEBUG = True

RARITY_RANKING = {
    "Amazing Rare": 5,
    "Common": 1,
    "LEGEND": 5,
    "Promo": 3,
    "Rare": 5,
    "Rare ACE": 5,
    "Rare BREAK": 5,
    "Rare Holo": 5,
    "Rare Holo EX": 5,
    "Rare Holo GX": 5,
    "Rare Holo LV.X": 5,
    "Rare Holo Star": 5,
    "Rare Holo V": 5,
    "Rare Holo VMAX": 7,
    "Rare Prime": 5,
    "Rare Prism Star": 7,
    "Rare Rainbow": 10,
    "Rare Secret": 7,
    "Rare Shining": 7,
    "Rare Shiny": 7,
    "Rare Shiny GX": 7,
    "Rare Ultra": 10,
    "Uncommon": 3,
    "ACE SPEC Rare": 5, 
    "Classic Collection": 5, 
    "Double Rare": 7, 
    "Hyper Rare": 8,
    "Illustration Rare": 6, 
    "Radiant Rare": 5, 
    "Rare Holo VSTAR": 7,
    "Shiny Rare": 7, 
    "Shiny Ultra Rare": 9, 
    "Special Illustration Rare": 9,
    "Trainer Gallery Rare Holo": 9, 
    "Ultra Rare": 10
}
