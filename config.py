from dotenv import load_dotenv
import os
from pokemontcgsdk import RestClient, Set
from threading import Thread
import asyncio

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

"""
Ranking Hierarchy

Common, Promo, None
Uncommon
Rare, Rare Holo, Rare Ace, Rare Prime
Lv X, GX, V, VMAX, double rare, Amazing Rare
BREAK, LEGEND, Shiny, Shining, VSTAR
Rare Rainbow, Rare Secret, Shiny GX, Rare Ultra
"""

RARITY_RANKING = {
    None: 1,
    'Common': 1,
    'Promo': 1,
    
    'Uncommon': 2,

    'Rare': 5,
    'Rare Holo': 5,
    'Rare ACE': 5,
    'Rare Prime': 5,
    'Classic Collection': 5,

    'Rare Holo LV.X': 7,
    'Rare Holo GX': 7,
    'Rare Holo EX': 7,
    'Rare Holo Star': 7,
    'Rare Prism Star': 7,
    'Rare Holo V': 7,
    'Rare Holo VMAX': 7,
    'Double Rare': 7,
    'Amazing Rare': 7,
    'ACE SPEC Rare': 7,

    'Rare BREAK': 10,
    'LEGEND': 10,
    'Shiny Rare': 10,
    'Rare Shiny': 10,
    'Rare Shining': 10,
    'Rare Holo VSTAR': 10,
    'Radiant Rare': 10,
    'Illustration Rare': 10,
    'Trainer Gallery Rare Holo': 10,

    'Rare Rainbow': 15,
    'Rare Secret': 15,
    'Rare Shiny GX': 15,
    'Rare Ultra': 15,
    'Ultra Rare':15,
    'Hyper Rare': 15,
    'Special Illustration Rare': 15,
    'Shiny Ultra Rare': 15,

}

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

background_loop = asyncio.new_event_loop()
Thread(target=run_async_loop, args=(background_loop,), daemon=True).start()
