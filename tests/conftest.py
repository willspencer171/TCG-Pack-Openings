import pytest
from config import SET_LIST_LOCATION
from random import choice
from pokemontcgsdk import Set
from src.pack_logic import Pack
import os

@pytest.fixture(scope='session')
def pack_for_testing():
    """Set code is picked at random from a list of sets. 
    This minimises API calls but requires updating when new sets release"""
    setlist_path = SET_LIST_LOCATION
    if not os.path.exists(setlist_path):
        packs = [set.id for set in Set.all()]
        with open(setlist_path, 'x') as f:
            f.write("\n".join(packs))

    with open(SET_LIST_LOCATION, 'r') as f:
        pack_ids = f.readlines()

    chosen_pack = choice(pack_ids)
    
    return Pack(chosen_pack)