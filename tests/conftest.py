import pytest
import config
from random import choice, choices
from pokemontcgsdk import Set
from src.model.pack_logic import Pack
import os

@pytest.fixture(scope='session')
def pack_for_testing():
    """Set code is picked at random from a list of sets. 
    This minimises API calls but requires updating when new sets release"""
    setlist_path = config.SET_LIST_LOCATION
    if not os.path.exists(setlist_path):
        packs = [set.id for set in Set.all()]
        with open(setlist_path, 'x') as f:
            f.write("\n".join(packs))

    with open(config.SET_LIST_LOCATION, 'r') as f:
        pack_ids = f.readlines()

    chosen_pack = choices(pack_ids, weights=list(range(len(pack_ids), 0, -1)), k=1)[0]
    
    return Pack(chosen_pack)

@pytest.fixture(scope='session')
def trainer_gallery_pack():
    sets = ['swsh9', 'swsh10', 'swsh11', 'swsh12', 'swsh12pt5']
    return Pack(choice(sets))
