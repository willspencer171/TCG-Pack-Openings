from __future__ import annotations  # deprecated in v3.14

from src.pack_logic import Pack, HashCard
from src.utils import debug_message
from config import INVENTORY_LOCATION, RARITY_RANKING, APP_CURRENCY

from collections import defaultdict
import pickle
from os import path
import pandas as pd

class Inventory:
    def __init__(self, reset_inv = False):
        if not reset_inv and path.exists(INVENTORY_LOCATION):
            inv = Inventory.open_inventory()
            self.packs_opened_ = inv.packs_opened
            self.cards_obtained_ = inv.cards_obtained
        else:
            debug_message('Resetting Inventory...')
            self.packs_opened_: defaultdict[Pack, int] = defaultdict(int)
            self.cards_obtained_: defaultdict[HashCard, int] = defaultdict(int)
    
    def __str__(self):
        return self.as_dataframe().__str__() + f'\n{self.inventory_summary()}'

    def save_inventory(self):
        if not path.exists(INVENTORY_LOCATION):
            with open(INVENTORY_LOCATION, 'xb') as file:
                pickle.dump(self, file)
        else:
            with open(INVENTORY_LOCATION, 'wb') as file:
                pickle.dump(self, file)

    @staticmethod
    def open_inventory() -> Inventory:
        if not path.exists(INVENTORY_LOCATION):
            debug_message('No inventory file found, please confirm '
                          f'existence of file {INVENTORY_LOCATION}', 'error')
        
        with open(INVENTORY_LOCATION, 'rb') as file:
            inv = pickle.load(file)
            return inv

    @property
    def packs_opened(self):
        return self.packs_opened_
    
    @property
    def cards_obtained(self):
        return self.cards_obtained_
    
    @property
    def size(self) -> tuple[int, int]:
        return (sum(self.cards_obtained.values()), sum(self.packs_opened.values()))
    
    def add_pack(self, pack: Pack):
        for card in pack:
            self.cards_obtained[card] += 1
        
        self.packs_opened[pack] += len(pack) // 10
        self.save_inventory()
    
    def add_card(self, card: HashCard):
        self.cards_obtained[card] += 1
        self.save_inventory()
    
    @property
    def total_estimated_value(self) -> float:

        df = self.as_dataframe()
        return float(round(df[
            ~(df['supertype'] == 'energy')]
            ['avg_price'].sum(), 2))

    def inventory_summary(self):
        total_cards = self.size[0]
        unique_cards = len(self.cards_obtained)
        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "total_price": self.total_estimated_value
        }
    
    def as_dataframe(self) -> pd.DataFrame:
        data = [{
            'id': card.id,
            'name': card.name,
            'number': card.number,
            'nat_dex_no': card.nationalPokedexNumbers,
            'rarity': card.rarity,
            'supertype': card.supertype,
            'set': card.set.name,
            'avg_price': card.price,
            'quality': card.quality,
            'quantity': qty,
            'artist': card.artist,
            'types': card.types
        }
        for card, qty in self.cards_obtained.items()]

        return pd.DataFrame(data)
