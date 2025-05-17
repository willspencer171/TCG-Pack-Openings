from dotenv import load_dotenv
import os
from pokemontcgsdk import RestClient, Set
from threading import Thread
import asyncio
import numpy as np

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
ranking_tiers = [
    ['Common', 'Promo', None],
    ['Uncommon'],
    ['Rare', 'Rare Holo', 'Rare ACE', 'Rare Prime', 'Classic Collection'],
    ['Rare Holo LV.X', 'Rare Holo GX', 'Rare Holo EX', 'Rare Holo Star', 'Rare Prism Star',
    'Rare Holo V', 'Rare Holo VMAX', 'Double Rare', 'Amazing Rare', 'ACE SPEC Rare'],
    ['Rare BREAK', 'LEGEND', 'Shiny Rare', 'Rare Shiny', 'Rare Shining', 'Rare Holo VSTAR',
    'Radiant Rare', 'Illustration Rare', 'Trainer Gallery Rare Holo'],
    ['Rare Rainbow', 'Rare Secret', 'Rare Shiny GX', 'Rare Ultra', 'Ultra Rare', 'Hyper Rare',
    'Special Illustration Rare', 'Shiny Ultra Rare']
]

def generate_ranking(decay: float=2):

    num_tiers = len(ranking_tiers)
    weights = np.linspace(0, decay, num=num_tiers)
    weights = np.exp(-weights)

    RARITY_RANKING = {}
    RARITY_PROBABILITIES = {}

    for index, (tier_labels, weight) in enumerate(zip(ranking_tiers, weights)):
        for label in tier_labels:
            RARITY_RANKING[label] = index
            RARITY_PROBABILITIES[label] = np.round(weight, 5)

    return RARITY_RANKING, RARITY_PROBABILITIES

RARITY_RANKING, RARITY_PROBABILITIES = generate_ranking()

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

background_loop = asyncio.new_event_loop()
Thread(target=run_async_loop, args=(background_loop,), daemon=True).start()
