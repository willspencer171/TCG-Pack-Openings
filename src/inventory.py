from src.pack_logic import Pack
from src.utils import debug_message
from config import INVENTORY_LOCATION
from collections import defaultdict
import pickle
from os import path

class Inventory:
    def __init__(self):
        self.packs_opened_ = defaultdict(int)
        self.cards_obtained_ = defaultdict(int)

    def save_inventory(self):
        pickle.dump(self, INVENTORY_LOCATION)

    def open_inventory(self):
        if not path.exists(INVENTORY_LOCATION):
            debug_message('No inventory file found, please confirm '
                          f'existence of file {INVENTORY_LOCATION}', 'error')
        
        return pickle.load(INVENTORY_LOCATION)

    @property
    def packs_opened(self):
        return self.packs_opened_
    
    @property
    def cards_obtained(self):
        return self.cards_obtained_
    
    def add_pack(self, pack: Pack):
        for card in pack:
            self.cards_obtained[card] += 1
        
        self.packs_opened[pack] += 1
