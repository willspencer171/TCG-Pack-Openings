from __future__ import annotations # Deprecated in Python 3.14

from src.utils import debug_message, download_pack_images
from config import RARITY_RANKING, APP_CURRENCY, CURRENCY_CONVERSIONS, setlist

import random

from pokemontcgsdk import Card, QueryBuilder, Set
from dataclasses import dataclass

@dataclass
class HashCard(Card):
    """HashCard dataclass ensures a hash table-like object can be used to
    keep track of obtained cards from pulls in the future"""

    quality: str
    qualities = ['normal', 'holofoil', 'reverseHolofoil', '1stEditionNormal', '1stEditionHolofoil']

    def __hash__(self):
        return hash(self.id + self.quality)
    
    def __eq__(self, other):
        return self.id == other.id
    
    @staticmethod
    def find(id) -> HashCard:
        return QueryBuilder(HashCard, HashCard.transform).find(id)
    
    @staticmethod
    def where(**kwargs) -> list[HashCard]:
        return QueryBuilder(HashCard, HashCard.transform).where(**kwargs)

    @staticmethod
    def all() -> list[HashCard]:
        return QueryBuilder(HashCard, HashCard.transform).all()
    
    @staticmethod
    def transform(response: dict):
        this_quals = []
        for qual in HashCard.qualities:
            if response.get('tcgplayer', {}).get('prices', {}).get(qual):
                response['tcgplayer']['prices'][qual] = {key: round(val * CURRENCY_CONVERSIONS[APP_CURRENCY], 2) 
                                                          for key, val in 
                                                          response['tcgplayer']['prices'].pop(qual).items()
                                                          if val}
                this_quals.append(qual)
        
        if len(this_quals) != 0:
            response['quality'] = random.choices(this_quals, weights=list(range(len(this_quals), 0, -1)))[0]
        else:
            response['quality'] = response.get('quality', 'normal')
        return response
    
    @property
    def price(self):
        return getattr(getattr(getattr(getattr(
            self, 'tcgplayer', None), 
            'prices', None), 
            self.quality, None), 
            'market', 0.0)

class Pack:
    ### Should be an abstract class implemented by each set? Maybe?
    ### Or just change the number of cards if it's a promo set

    # What does a pack need to have?
    # 1 energy card
    # 9 Other cards
    # Last card is guaranteed at least rare (rank 5)

    def __init__(self, set_id, ten_pack=False):
        self.set_id = set_id
        self.ten_pack = ten_pack
        self.set: Set = Set.find(set_id)
        self.pack_items: list[HashCard | None]
        self.available: list[HashCard | None]
        self.pick_cards()
    
    def __str__(self):
        return f'{self.set.name}'

    def pick_cards(self):
        debug_message(f"Fetching cards from {self.set.name}...")
        self.available = HashCard.where(q=f'set.id:{self.set_id} rarity:*')
        if len(self.available) != 0:
            if any([s in [self.set.id + "gg", self.set.id + "tg"] for s in setlist]):
                debug_message('Adding gallery set')
                self.available += HashCard.where(q=f'set.id:{self.set_id}*g rarity:*')
            debug_message("Set cards retrieved!")
            high_rarity = [card for card in self.available if
                       RARITY_RANKING[card.rarity] >= 5]
        else:
            debug_message('Set has no rarity info, probs a promo')
            self.available = HashCard.where(q=f'set.id:{self.set_id}')
            high_rarity = self.available
        
        energies = [card for card in self.available if 
                    card.supertype == 'energy'
                    and 'basic' in card.subtypes and
                    not any(rarity in card.rarity for 
                            rarity in ['secret', 'hyper', None])]
        
        for card in energies:
            if card in self.available:
                self.available.remove(card)

        if self.ten_pack:
            n_standard = 80
            n_high = 10
            n_energy = 10
        else:
            n_standard = 8
            n_high = 1
            n_energy = 1

        if len(energies) == 0:
            debug_message("No basic Energies in set, looking in series")
            query = (f'set.series:"{self.set.series}" supertype:energy subtypes:basic '
                      '-rarity:*secret* -rarity:*hyper* -rarity:*holo*')
            energies = HashCard.where(q=query)
            if len(energies) > 0:
                debug_message("Basic energies found")
            else:
                debug_message(f"No energies found in series {self.set.series}")
                ### Search through series around
                match self.set.series:
                    case "POP":
                        energies = HashCard.where(q=(f'set.series:"EX" supertype:energy subtypes:basic -rarity:*holo*'))
                        
                    case "Other":
                        energies = HashCard.where(q=(f'set.series:"Sword & Shield" supertype:energy '
                                                     'subtypes:basic -rarity:*secret*'))

                    case "Platinum":
                        energies = HashCard.where(q=(f'set.series:"Diamond & Pearl" supertype:energy subtypes:basic'))

        debug_message(f'Got {len(energies)} energies')
        # Add Energy card for first card
        self.pack_items = random.choices(energies, k=n_energy)

        debug_message(f'Got {len(self.available)} cards, with {len(high_rarity)} high rank')
        # Pick 9 cards
        self.pack_items = self.pack_items + sorted(Pack._draw_random(self.available, n_standard) + Pack._draw_random(high_rarity, n_high), 
                                                   key=lambda x: RARITY_RANKING[x.rarity] + 
                                                                 HashCard.qualities.index(x.quality))
    
    @staticmethod
    def _draw_random(card_pool: list[HashCard], k=1):
        weights = {rarity: 1 / rank for rarity, rank in RARITY_RANKING.items()}
        card_ranks = [weights[card.rarity] for card in card_pool]

        cards = random.choices(card_pool, 
                               weights=card_ranks,
                               k=k)
        return cards
    
    async def get_pack_images(self):
        pack_image_urls = [card.images.small for card in self.pack_items]
        self.image_data = await download_pack_images(pack_image_urls)
    
    def print_pack(self):
        for card in self.pack_items:
            print(f"{card.name}: {card.rarity}")

    def __len__(self):
        return len(self.pack_items)
    
    def __iter__(self):
        yield from self.pack_items

    def __getitem__(self, index):
        return self.pack_items[index]
    
    def __hash__(self):
        return hash(self.set_id)

    def __eq__(self, other):
        return self.set_id == other.set_id

class PromoPack(Pack):
    @staticmethod
    def _draw_random():
        raise NotImplementedError
    
    def pick_cards(self):
        # 4 cards in pack
        pass
