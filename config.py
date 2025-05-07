from dotenv import load_dotenv
import os
from pokemontcgsdk import RestClient, Set

if not os.path.exists('.env'):
    open('.env', 'w').close()

load_dotenv()

API_KEY = os.getenv('API_KEY')
SET_LIST_LOCATION = os.getenv('SET_LIST_LOCATION')
INVENTORY_LOCATION = os.getenv('INVENTORY_LOCATION')
APP_CURRENCY = os.getenv('APP_CURRENCY')

CURRENCY_CONVERSIONS = {
            'USD': 1,
            'GBP': 0.75,
            'EUR': 0.88
        }

for env_key in [API_KEY, SET_LIST_LOCATION, INVENTORY_LOCATION, APP_CURRENCY]:
    if not env_key:
        raise ValueError(f"{env_key} is missing! Please check .env file")

RestClient.configure(API_KEY)

DEBUG = True

setlist = [s.id for s in Set.all()]
with open(SET_LIST_LOCATION, 'w') as f:
    f.write('\n'.join(setlist))

RARITY_RANKING = {
    "Amazing Rare": 5,
    "Common": 1,
    "LEGEND": 5,
    "Promo": 1,
    "Rare": 5,
    "Rare ACE": 5,
    "Rare BREAK": 5,
    "Rare Holo": 5,
    "Rare Holo EX": 7,
    "Rare Holo GX": 7,
    "Rare Holo LV.X": 7,
    "Rare Holo Star": 7,
    "Rare Holo V": 7,
    "Rare Holo VMAX": 8,
    "Rare Prime": 6,
    "Rare Prism Star": 7,
    "Rare Rainbow": 10,
    "Rare Secret": 7,
    "Rare Shining": 8,
    "Rare Shiny": 8,
    "Rare Shiny GX": 9,
    "Rare Ultra": 10,
    "Uncommon": 3,
    "ACE SPEC Rare": 7, 
    "Classic Collection": 6, 
    "Double Rare": 6, 
    "Hyper Rare": 8,
    "Illustration Rare": 7, 
    "Radiant Rare": 6, 
    "Rare Holo VSTAR": 8,
    "Shiny Rare": 7, 
    "Shiny Ultra Rare": 9, 
    "Special Illustration Rare": 9,
    "Trainer Gallery Rare Holo": 9, 
    "Ultra Rare": 7,
    None: 1
}
