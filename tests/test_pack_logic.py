from src.pack_logic import HashCard, Pack
import pytest
import os
import pickle  

@pytest.fixture(scope='session')
def pack_for_testing():
    return Pack('sv8')

@pytest.mark.skip('too many calls to API')
def test_hash_card_is_hashable():
    hashcard = HashCard.find('xy1-1')
    assert hashcard is not None
    h = hash(hashcard)
    print(h)
    assert h

def test_pack_returns_10_cards(pack_for_testing):
    assert len(pack_for_testing) == 10

    for card in pack_for_testing:
        print(f'{card.name} - {card.rarity}')

def test_last_card_is_rare(pack_for_testing):
    assert pack_for_testing[-1].rarity not in ['Common', 'Uncommon']
