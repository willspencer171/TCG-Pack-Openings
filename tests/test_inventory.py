from src.inventory import *

def test_inventory_adds_pack(pack_for_testing):
    inv = Inventory()
    inv.add_pack(pack_for_testing)
    assert inv.packs_opened[pack_for_testing] == 1
    assert all([card in pack_for_testing for card in inv.cards_obtained])
    