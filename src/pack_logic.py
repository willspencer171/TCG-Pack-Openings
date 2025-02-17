from __future__ import annotations
from typing import Self

from utils import debug_message

import random

from pokemontcgsdk import Card, QueryBuilder, Set
from dataclasses import dataclass

RARITY_RANKING = {
    "Amazing Rare": 5,
    "Common": 1,
    "LEGEND": 5,
    "Promo": 2,
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
    "Uncommon": 2
}

@dataclass
class HashCard(Card):
    """HashCard dataclass ensures a hash table-like object can be used to
    keep track of obtained cards from pulls"""
    def __hash__(self):
        return hash(self.id)
    
    @staticmethod
    def find(id) -> Self:
        return QueryBuilder(HashCard, HashCard.transform).find(id)
    
    @staticmethod
    def where(**kwargs) -> list[HashCard]:
        return QueryBuilder(HashCard, HashCard.transform).where(**kwargs)

    @staticmethod
    def all() -> list[Self]:
        return QueryBuilder(HashCard, HashCard.transform).all()
    
    @staticmethod
    def transform(response):
        if response.get('tcgplayer', {}).get('prices', {}).get('1stEditionNormal'):
            response['tcgplayer']['prices']['firstEditionNormal'] = response['tcgplayer']['prices'].pop('1stEditionNormal')
        if response.get('tcgplayer', {}).get('prices', {}).get('1stEditionHolofoil'):
            response['tcgplayer']['prices']['firstEditionHolofoil'] = response['tcgplayer']['prices'].pop('1stEditionHolofoil')
        return response

class Pack:
    ### Should be an abstract class implemented by each set? Maybe?
    ### Or just change the number of cards if it's a mcdonald's set

    # What does a pack need to have?
    # 1 energy card
    # 0-3 Trainer Cards
    # 6-9 Pokemon Cards

    # Chances of higher rarity cards increase as card number increases

    # Are Cards hashable? They are now!
    def __init__(self, set_id):
        self.set_id = set_id
        self.set = Set.find(set_id)
        self.pack_items = self.pick_cards()

    def pick_cards(self) -> list[HashCard]:
        available = HashCard.where(q=f'set.id:{self.set_id}')

        debug_message("Set cards found")

        energies = [card for card in available if card.supertype == 'energy' and card.subtypes == 'basic']
        for card in available:
            if card in energies:
                available.remove(card)

        if len(energies) == 0:
            debug_message("No basic Energies in set, looking in series")
            energies = HashCard.where(q=f'set.series:"{self.set.series}" supertype:energy subtypes:basic -rarity:*secret')
            if len(energies) > 0:
                debug_message("Basic energies found")
            else:
                debug_message("No energies, found", 'error')

        # Add Energy card for first card
        card = random.choice(energies)
        self.pack_items.append(card)

        # Pick 9 cards
        self.pack_items = self.pack_items + Pack.draw_random(available, 9)
    
    @staticmethod
    def _draw_random(card_pool, k):
        weights = {rarity: 1 / rank for rarity, rank in RARITY_RANKING.items()}
        card_ranks = [weights[card.rarity] for card in card_pool]

        cards = random.choices(card_pool, 
                               weights=card_ranks,
                               k=k)
        return sorted(cards, key=lambda x: RARITY_RANKING[x.rarity])
    
    def __len__(self):
        return len(self.pack_items)
