from src.inventory import *
from config import INVENTORY_LOCATION
from pytest import skip

from os.path import getmtime
from datetime import datetime as dt
from datetime import timedelta as td

def test_inventory_adds_pack(pack_for_testing):
    inv = Inventory(reset_inv=True)
    inv.add_pack(pack_for_testing)
    assert inv.packs_opened[pack_for_testing] == 1
    assert all([card in pack_for_testing for card in inv.cards_obtained])

def test_inventory_size(pack_for_testing):
    inv = Inventory(reset_inv=True)
    inv.add_pack(pack_for_testing)
    inv.add_pack(pack_for_testing)
    size = inv.size
    assert size[0] == 20 and size[1] == 2

@skip
def test_inventory_score(pack_for_testing):
    inv = Inventory()
    inv.add_pack(pack_for_testing)
    score = inv.total_score
    print(f"Score: {score}")
    assert isinstance(score, int) and score > 0

def test_inventory_saves_and_loads(pack_for_testing):
    inv = Inventory()
    inv.add_pack(pack_for_testing)
    inv.save_inventory()
    assert dt.fromtimestamp(getmtime(INVENTORY_LOCATION)) >= dt.now() - td(milliseconds=5)    # test it was saved recently
    inv = Inventory.open_inventory()
    assert inv is not None

def test_inventory_price():
    inv = Inventory()
    value = inv.total_estimated_value
    assert isinstance(value, float) and value > 0
