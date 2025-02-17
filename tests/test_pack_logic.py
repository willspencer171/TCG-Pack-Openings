from src.pack_logic import HashCard, Pack
import pytest

@pytest.mark.skip('too many calls to API')
def test_hash_card_is_hashable():
    hashcard = HashCard.find('xy1-1')
    assert hashcard is not None
    h = hash(hashcard)
    print(h)
    assert h

def test_pack_returns_10_cards():
    pack = Pack("swsh1")
    assert len(pack) == 10
