from src.pack_logic import HashCard
from config import RARITY_RANKING

def test_pack_is_indexable(pack_for_testing):
    assert pack_for_testing[0] is not None

def test_pack_is_iterable(pack_for_testing):
    for card in pack_for_testing:
        assert card

def test_pack_contains_cards_only(pack_for_testing):
    for card in pack_for_testing:
        assert isinstance(card, HashCard)

def test_hash_card_is_hashable(pack_for_testing):
    hashcard = pack_for_testing[0]
    assert hashcard is not None
    assert hash(hashcard)

def test_pack_returns_10_cards(pack_for_testing):
    assert len(pack_for_testing) == 10

    for card in pack_for_testing:
        print(f'{card.name} - {card.rarity}')

def test_last_card_is_rare(pack_for_testing):
    assert RARITY_RANKING[pack_for_testing[-1].rarity] >= 5

def test_pack_can_have_trainer_gallery(trainer_gallery_pack):
    ids = [card.set.id for card in trainer_gallery_pack.available]
    assert any(gallery in setid for gallery in ['tg', 'gg'] for setid in ids)
